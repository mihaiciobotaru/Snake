import numpy as np
from app import GameApp

class Q_learning:
    def __init__(self, gamma=0.9, alpha=0.1, epsilon=0.1):
        self.gamma = gamma
        self.alpha = alpha
        self.epsilon = epsilon
        q_table = np.zeros((41, 41, 41, 41, 41, 41, 41, 41, 41, 41, 41, 41, 5))
        # q table has 13 dimensions .


        self.state = None
        self.action = None

    def choose_action(self, state):
        self.state = state
        if np.random.uniform(0, 1) < self.epsilon:
            self.action = np.random.choice([0, 1, 2, 3])
        else:
            print(self.q_table)
            print(state)
            state = np.array(state)
            print(state.shape)
            #self.action = np.argmax(self.q_table[state])
        action = np.array(self.action)
        print(action.shape)
        exit()
        return self.action
    
    def predict(self, state):
        return self.choose_action(state)

    def learn(self, reward, next_state):

        predict = self.q_table[self.state, self.action]
        target = reward + self.gamma * np.max(self.q_table[next_state])
        self.q_table[self.state, self.action] += self.alpha * (target - predict)
        
        self.state = None
        self.action = None
    
    def train(self, episodes=1000):

        for episode in range(episodes):
            app = GameApp(True, "q_learning")
            app.set_ai_model(self)
            score, moves = app.runGame()
            if episode % 1 == 0:
                print(f"Episode: {episode}, Score: {score}, Moves: {moves}")

        self.test()

    def test(self):
        app = GameApp(False, "q_learning")
        app.set_ai_model(self)
        score, moves = app.runGame()
        print(f"Score: {score}, Moves: {moves}")