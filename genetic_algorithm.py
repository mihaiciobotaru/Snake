# class for training ANN to play the game

import time
from ann import SnakeANN
from app import GameApp
import numpy as np
import threading
import struct

class GeneticAlgorithm:
    population_size = 0
    mutation_rate = 0
    crossover_rate = 0
    playing_model = False

    population = []

    def save_model(self, model, filename):
        model.save(filename)

    def __init__(self, population_size, mutation_rate, crossover_rate):
        self.population_size = population_size
        self.mutation_rate = mutation_rate
        self.crossover_rate = crossover_rate
        self.population = [SnakeANN().randomize() for i in range(population_size)]

    def get_fitness_of_individual(self, individual, results, index):
        app = GameApp(True, "ai")
        app.set_ann_model(individual)
        score, moves = app.runGame()
        fitness = 10 * moves + (2 ** score + (score ** 2.1) * 500) - ((score ** 1.2) * ((moves * 0.25)) ** 1.3)    
        results[index] = fitness

    def crossover(self, parent1, parent2):
        parent1_weights = parent1.get_weights()
        parent2_weights = parent2.get_weights()
        parent1_flat_weights, parent1_original_shapes = self.weights_to_1d_array(parent1_weights)
        parent2_flat_weights, parent2_original_shapes = self.weights_to_1d_array(parent2_weights)
        # make the weights arrays 1d array with bits

        parent1_weights_bits = [self.float32_to_bits_array(weight) for weight in parent1_flat_weights]
        parent2_weights_bits = [self.float32_to_bits_array(weight) for weight in parent2_flat_weights]

        parent1_weights_bits = np.array(parent1_weights_bits)
        parent2_weights_bits = np.array(parent2_weights_bits)
        original_shape = parent1_weights_bits.shape

        parent1_weights_bits = parent1_weights_bits.flatten()
        parent2_weights_bits = parent2_weights_bits.flatten()

        # crossover

        lhs = np.random.randint(0, len(parent1_weights_bits))
        rhs = np.random.randint(0, len(parent1_weights_bits))

        if lhs > rhs:
            lhs, rhs = rhs, lhs

        child1_weights_bits = np.concatenate((parent1_weights_bits[:lhs], parent2_weights_bits[lhs:rhs], parent1_weights_bits[rhs:]))
        child1_weights_bits = child1_weights_bits.reshape(original_shape)

        child2_weights_bits = np.concatenate((parent2_weights_bits[:lhs], parent1_weights_bits[lhs:rhs], parent2_weights_bits[rhs:]))
        child2_weights_bits = child2_weights_bits.reshape(original_shape)

        child1_weights = [self.bits_array_to_float32(weight) for weight in child1_weights_bits]
        child2_weights = [self.bits_array_to_float32(weight) for weight in child2_weights_bits]

        child1_weights = np.array(child1_weights)
        child2_weights = np.array(child2_weights)

        child1_weights = self.one_d_array_to_weights(child1_weights, parent1_original_shapes)
        child2_weights = self.one_d_array_to_weights(child2_weights, parent2_original_shapes)

        child1 = SnakeANN().set_weights(child1_weights)
        child2 = SnakeANN().set_weights(child2_weights)

        return child1, child2
    
    def weights_to_1d_array(self, weights_list):
        # Flatten the weights to a one-dimensional array and store original shapes
        flat_weights = []
        original_shapes = []
        for weights in weights_list:
            original_shapes.append(weights.shape)
            flat_weights.extend(weights.flatten())

        flat_weights = np.array(flat_weights)
        return flat_weights, original_shapes
    
    def save_model(self, model, filename):
        model.save_model(filename)
    
    def one_d_array_to_weights(self, flat_weights, original_shapes):
        # Convert the one-dimensional array back to the original shapes
        weights_list = []
        start = 0
        for shape in original_shapes:
            size = np.prod(shape)
            weights = flat_weights[start:start + size].reshape(shape)
            weights_list.append(weights)
            start += size

        return weights_list
    

    def mutate(self, individual):
        # iterate through each individual value of the weights
        weights = individual.get_weights()
        one_d_weights, original_shapes = self.weights_to_1d_array(weights)

        for i in range(len(one_d_weights)):
            bits_array = self.float32_to_bits_array(one_d_weights[i])
            for j in range(len(bits_array)):
                if np.random.rand() < self.mutation_rate:
                    bits_array[j] = 1 - bits_array[j]

            one_d_weights[i] = self.bits_array_to_float32(bits_array)

        weights = self.one_d_array_to_weights(one_d_weights, original_shapes)
        individual.set_weights(weights)
        return individual

    
    
    def select_individuals(self, fitnesses):
        fitnesses = ((fitnesses - np.min(fitnesses)) * 2) / (np.max(fitnesses) - np.min(fitnesses) + 1) - 1
        fitnesses = [1 / (1 + np.exp(-fitness)) for fitness in fitnesses]
        total_fitness = sum(fitnesses)
        probabilities = [fitness / total_fitness for fitness in fitnesses]

        selected_individuals = []
        for i in range(self.population_size):
            selected_individuals.append(np.random.choice(self.population, p=probabilities))

        return selected_individuals
    
    def get_fitnesses(self):
        #fitnesses = [self.get_fitness_of_individual(individual) for individual in self.population]
        # use multiprocessing to speed up the process
        fitnesses = [0] * self.population_size
        threads = []
        for i in range(self.population_size):
            thread = threading.Thread(target=self.get_fitness_of_individual, args=(self.population[i], fitnesses, i))
            threads.append(thread)
            thread.start()

        for i in range(self.population_size):
            threads[i].join()

        return fitnesses

    def next_generation(self, gen_count):
        fitnesses = self.get_fitnesses()
        print("Generation ", gen_count, "Fitnesses: ", fitnesses)
        # save best model
        best_individual = self.population[np.argmax(fitnesses)]
        self.save_model(best_individual, f"./models/best_model_gen_{gen_count}.h5")
        print(f"Playing best model of generation {gen_count} with fitness {np.max(fitnesses)}")
        play_thread = threading.Thread(target=self.play_model, args=(best_individual, gen_count))
        play_thread.start()

        new_population = self.select_individuals(fitnesses)
        crossover_rate = self.crossover_rate
        for i in range(0, len(new_population), 2):
            if np.random.rand() < crossover_rate:
                child1, child2 = self.crossover(new_population[i], new_population[i + 1])
                new_population[i] = child1
                new_population[i + 1] = child2

        for i in range(0, len(new_population)):
            index = np.random.randint(0, len(new_population))
            new_population[index] = self.mutate(new_population[index])
        self.population = new_population
        return self.population
    
    def train(self, generations):
        for i in range(generations):
            self.next_generation(i)

    def float32_to_bits_array(self, value):
        # Pack float into bytes
        packed = struct.pack('!f', value)
        # Convert bytes to integer
        int_value = int.from_bytes(packed, byteorder='big')
        # Convert integer to binary string and pad to 32 bits
        binary_string = f'{int_value:032b}'
        # Convert binary string to a list of integers (bit array)
        bits_array = [int(bit) for bit in binary_string]
        return bits_array

    def bits_array_to_float32(self, bits_array):
        # Convert bits array to binary string
        binary_string = ''.join(str(bit) for bit in bits_array)
        # Convert binary string to integer
        int_value = int(binary_string, 2)
        # Convert integer to bytes
        packed = int_value.to_bytes(4, byteorder='big')
        # Unpack bytes to float
        value = struct.unpack('!f', packed)[0]
        return value
    
    def play_model(self, model, generation):
        while self.playing_model:
            time.sleep(1)

        self.playing_model = True
        app = GameApp(False, "ai", f" Generation {generation}")
        app.set_ann_model(model)
        score, moves = app.runGame()
        print("Generation", generation, "Score: ", score, "Moves: ", moves)
        self.playing_model = False
            

            