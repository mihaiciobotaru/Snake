import tensorflow as tf
import numpy as np
from app import GameApp
import pygame
from pygame import gfxdraw

class NeuralNetwork(tf.keras.Model):
    last_draw = None
    learning_rate = 0.01
    discount_factor = 0.5
    exploration_rate = 1
    exploration_decay = 1/5000
    min_exploration_rate = 0.00

    def __init__(self):
        super(NeuralNetwork, self).__init__()
        self.input_layer = tf.keras.layers.Dense(12, activation='relu')
        self.hidden_layer1 = tf.keras.layers.Dense(12, activation='relu')
        self.hidden_layer2 = tf.keras.layers.Dense(12, activation='relu')
        self.hidden_layer3 = tf.keras.layers.Dense(12, activation='relu')
        self.output_layer = tf.keras.layers.Dense(4, activation='softmax')
        self.loss_fn = tf.keras.losses.MeanSquaredError()
        self.optimizer = tf.keras.optimizers.Adam(learning_rate=self.learning_rate)

    def q_values(self, state):
        state = np.array(state).reshape(1, 12)
        x = self.input_layer(state)
        x = self.hidden_layer1(x)
        x = self.hidden_layer2(x)
        x = self.hidden_layer3(x)
        return self.output_layer(x)
    
    def take_action(self, state):
        self.state = state
        if np.random.rand() < self.exploration_rate:
            self.action = np.random.randint(0, 4)
        else:
            self.action = np.argmax(self.q_values(self.state))
        return self.action            
    
    def learn(self, reward, done, next_state):
        if self.state is None:
            return
        with tf.GradientTape() as tape:
            current_q_values = self.q_values(self.state)
            next_q_values = self.q_values(next_state)
            max_next_q = tf.reduce_max(next_q_values, axis=-1)
            target_q_values = current_q_values.numpy()
            print("______________")
            # if done:
            #     print("DEATH")
            print(self.state)
            print(target_q_values)
            print(reward, self.discount_factor, max_next_q, done)
            delta = reward + self.discount_factor * max_next_q * (1 - done)
            # every action that is not self.action reduce delta/3 and to self.action add delta
            target_q_values[0][self.action] += delta

            # print(target_q_values)
            # print(current_q_values)
            #if done:
                #exit()
            loss = self.loss_fn(current_q_values, target_q_values)
 
        gradients = tape.gradient(loss, self.trainable_variables)
        self.optimizer.apply_gradients(zip(gradients, self.trainable_variables))
        # current_q_values = self.q_values(self.state)
        # print(current_q_values)
        self.state = None
        self.action = None

    def visualize_network(self, window, update=False):

        if update:
            last_state = self.state
            last_decision = self.q_values(last_state).numpy().reshape(4)
            self.last_draw = (last_state, last_decision)
        else:
            last_state, last_decision = self.last_draw   
        
        distance_between_neurons = 16
        
        # compute distance between layers
        network_layers = self.layers
        network_layers_count = len(network_layers)
        x_start = 550
        neuron_size = 7
        
        window_width, window_height = pygame.display.get_surface().get_size()
        screen_division = (window_width - x_start) / (network_layers_count)
        STEP_SIZE = 1
        step = 0
        for i in range(network_layers_count):
            for j in range(network_layers[i].units):
                y = int(window_height / 2 + (j * distance_between_neurons) - (network_layers[i].units - 1)/2 * distance_between_neurons)
                x = int(x_start + step * screen_division)
                
                fill_factor = 0
                if i == 0:
                    fill_factor = int(last_state[j] * 255)
                elif i == network_layers_count - 1:
                    fill_factor = int(last_decision[j] * 255)

                # if fill factore is close to 0 make it white, below 0 make it red and above 0 blue

                if fill_factor < 0:
                    fill_factor = 0
                elif fill_factor > 255:
                    fill_factor = 255

                    
                # draw connections
                if i < network_layers_count - 1:
                    for k in range(network_layers[i + 1].units):
                        y2 = int((window_height / 2) + (k * distance_between_neurons) - (network_layers[i + 1].units - 1)/2 * distance_between_neurons)
                        x2 = int(x_start + (step + STEP_SIZE) * screen_division)
                        
                        fill_factor_line = 60
                        # input layer
                        if i == 0:
                            fill_factor_line = fill_factor / 2 + 40
                        
                        pygame.draw.line(window, (fill_factor_line, fill_factor_line, fill_factor_line), (x, y), (x2, y2), 1)
                        #gfxdraw.line(window,x + 2, y, x2, y2, (fill_factor_line, fill_factor_line, fill_factor_line, fill_factor_line))
                
                # gfxdraw.filled_circle(window, x, y, neuron_size, (fill_factor, fill_factor, fill_factor))
                # gfxdraw.aacircle(window, x, y, neuron_size, (255, 255, 255))
                pygame.draw.circle(window, (fill_factor, fill_factor, fill_factor), (x, y), neuron_size)
                pygame.draw.circle(window, (255, 255, 255), (x, y), neuron_size, 1)
            step += STEP_SIZE

class DeepQLearning:
    def __init__(self):
        self.model = NeuralNetwork()
    
    def predict(self, state):
        return self.model.take_action(state) + 1

    def learn(self, reward, done, next_state):
        self.model.learn(reward, done, next_state)
    
    def train(self, episodes=1000):

        for episode in range(episodes):
            app = GameApp(True, "q_learning")
            app.set_ai_model(self)
            score, moves = app.runGame()
            self.model.exploration_rate = max(self.model.min_exploration_rate, self.model.exploration_rate - self.model.exploration_decay)
            if episode % 200 == 0:
                print(f"Episode: {episode}, Score: {score}, Moves: {moves}")
                self.test()

    def visualize_network(self, window, update=False):
        self.model.visualize_network(window, update)

    def test(self):
        temp = self.model.exploration_rate
        self.model.exploration_rate = 0
        app = GameApp(False, "q_learning")
        app.set_ai_model(self)
        score, moves = app.runGame()
        print(f"Score: {score}, Moves: {moves}")
        self.model.exploration_rate = temp
        exit()

    
    