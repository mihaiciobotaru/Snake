from app import GameApp
from ann import SnakeANN
from genetic_algorithm import GeneticAlgorithm
from deep_q_learning import DeepQLearning

if __name__ == "__main__":
    # GA = GeneticAlgorithm(100, 0.6, 0.6)
    # GA.train(100)

    # model = SnakeANN()
    # #model.load_saved_model("./models/best_model_gen_5.h5")
    # model.load_saved_model("./models/bad_model_0_3_4_0_15.h5")
    # app = GameApp(False, "ai")
    # app.set_ann_model(model)
    # app.set_initial_fruit_position((0, 15))
    # score, moves = app.runGame()
    # print("Score: ", score, "Moves: ", moves)

    q_learning = DeepQLearning()
    q_learning.train(100000)
