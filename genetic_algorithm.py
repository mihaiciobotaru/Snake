# class for training ANN to play the game

import random
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

    def play_game_in_parallel(self, app, results, index, model):
        app = GameApp(True, "ai")
        app.set_ann_model(model)
        score, moves = app.runGame()
        score -= 3
        # if moves < 6:
        #     print("Suspected bad model:")
        #     print(app.initialFruitPosition)
        #     print(score, moves)
        #     self.save_model(model, f"./models/bad_model_{index}_{score}_{moves}_{app.initialFruitPosition.x}_{app.initialFruitPosition.y}.h5")
        #     exit()
        results[index] = (score, moves)

    def get_fitness_of_individual(self, individual, results, index):
        play_count = 5
        results_individual = [(0, 0) for i in range(play_count)]
        threads = []
        for i in range(play_count):
            thread = threading.Thread(target=self.play_game_in_parallel, args=(GameApp(True, "ai"), results_individual, i, individual))
            thread.start()
            threads.append(thread)

        for i in range(play_count):
            threads[i].join()


        mean_moves = np.mean([result[1] for result in results_individual])
        max_moves = np.max([result[1] for result in results_individual])
        std_moves = np.std([result[1] for result in results_individual])

        mean_score = np.mean([result[0] for result in results_individual])
        max_score = np.max([result[0] for result in results_individual])
        std_score = np.std([result[0] for result in results_individual])
      
        # fitness = \
        #     mean_score ** 1.5 + max_score ** 10 - std_score * 5 + \
        #     mean_moves ** 1.2 - (mean_score * 2 - mean_moves) ** 2 + \
        #     max_moves * 10 - std_moves * 5

        fitness = mean_moves + ( 2 ** mean_score + ((mean_score ** 2.1) * 500))\
        - ( (mean_score ** 1.2) * ((0.25 * mean_moves) ** 1.3))
        fitness = int(fitness)
        results[index] = fitness
        individual.set_score(results_individual)

    def crossover(self, parent1, parent2):
        parent1_weights = parent1.get_weights()
        parent2_weights = parent2.get_weights()

        parent1_weights, parent1_shapes = self.weights_to_1d_array(parent1_weights)
        parent2_weights, parent2_shapes = self.weights_to_1d_array(parent2_weights)
        
        child1_weights = []
        child2_weights = []

        for i in range(len(parent1_weights)):
            if np.random.rand() < 0.5:
                child1_weights.append(parent1_weights[i])
                child2_weights.append(parent2_weights[i])
            else:
                child1_weights.append(parent2_weights[i])
                child2_weights.append(parent1_weights[i])
        
        child1_weights = np.array(child1_weights)
        child2_weights = np.array(child2_weights)

        child1_weights = self.one_d_array_to_weights(child1_weights, parent1_shapes)
        child2_weights = self.one_d_array_to_weights(child2_weights, parent2_shapes)

        parent1.set_weights(child1_weights)
        parent2.set_weights(child2_weights)

        return parent1, parent2
    
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
            if np.random.rand() < self.mutation_rate:
                # mutate the weight
                one_d_weights[i] = random.uniform(-1, 1)

        weights = np.array(one_d_weights)
        weights = self.one_d_array_to_weights(one_d_weights, original_shapes)
        individual.set_weights(weights)
        return individual

    
    
    def select_individuals(self, fitnesses):
        # higher fitness is better
        selected_individuals = []
        for i in range(self.population_size):
            index = np.random.choice(range(self.population_size), p=fitnesses / np.sum(fitnesses))
            selected_individuals.append(self.population[index])
        
        return selected_individuals
    

    
    def get_fitnesses(self):
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
        print(f"Playing best model of generation {gen_count} with fitness {np.max(fitnesses)} and results {best_individual.results}")
        self.play_model(best_individual, gen_count)

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
        app.setGameSpeed(8)
        score, moves = app.runGame()
        print("Generation", generation, "Score: ", score, "Moves: ", moves)
        self.playing_model = False
            

            