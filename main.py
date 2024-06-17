from app import GameApp
from ann import SnakeANN
from genetic_algorithm import GeneticAlgorithm

if __name__ == "__main__":
    GA = GeneticAlgorithm(50, 0.7, 0.6)
    GA.train(100)

    # model = SnakeANN()
    # model.load_saved_model("./models/best_model_gen_9.h5")
    # app = GameApp(False, "ai")
    # app.set_ann_model(model)
    # score, moves = app.runGame()
    # print("Score: ", score, "Moves: ", moves)
