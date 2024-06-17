# ANN will have 3 layers: input, hidden, output
# Input layer: 24 neurons (8 directions * 3 possible values)
# Hidden layer: 12 neurons
# Output layer: 4 neurons (4 directions)

import numpy as np
import tensorflow as tf
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3' 

class SnakeANN:
    model = None

    def __init__(self):
        # create the model as described above
        initializer = tf.keras.initializers.RandomNormal(mean=0., stddev=1.)
        self.model = tf.keras.models.Sequential([
            tf.keras.layers.Dense(12, input_shape=(24,), activation='relu', kernel_initializer=initializer),
            tf.keras.layers.Dense(4, activation='softmax', kernel_initializer=initializer)
        ])
        self.model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])

    def randomize(self):
        self.model.set_weights([np.random.rand(*w.shape) for w in self.model.get_weights()])
        return self
    
    def set_weights(self, weights):
        self.model.set_weights(weights)
        return self

    def predict(self, input):
        input = np.array(input).reshape(1, 24)
        result = self.model.predict(input, verbose=0)
        return np.argmax(result) + 1
    
    def get_weights(self):
        return self.model.get_weights()
    
    def save_model(self, filename):
        self.model.save(filename)

    def load_saved_model(self, filename):
        self.model = tf.keras.models.load_model(filename)
        return self
    
    