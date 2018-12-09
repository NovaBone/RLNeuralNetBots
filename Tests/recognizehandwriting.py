from src.NeuralNetwork.neuralnetwork import *
from src.NeuralNetwork.costfunction import *
from src.NeuralNetwork.trainer import *
from src.utils import *
import pickle
import gzip
from numpy import *


def load_data():
    f = gzip.open('.../src/Tests/mnist.pkl.gz', 'rb')
    training_data, validation_data, test_data = pickle.load(f, encoding="bytes")
    f.close()
    return training_data, validation_data, test_data


network = NeuralNetwork([784, 16, 16, 10])
costFunction = SquareOfDifference()
trainer = BackpropagateTrainer(network, costFunction)

data = load_data()[0]
print("Loaded data")
digitImages = data[0].tolist()
trueVals = data[1].tolist()
costInputs, statsInputs = [], []
generationCosts = []
amountPerGen = 10
for index in range(len(digitImages)):
    generationCosts.append(CategoricalDataPiece(matrix(digitImages[index]).reshape((784,1)), trueVals[index], 10))
    if len(generationCosts) == amountPerGen:
        costInputs.append(generationCosts)
        if len(statsInputs) < 100:
            statsInputs.extend(generationCosts)
        generationCosts = []

print("Starting training")
train(trainer, costInputs)
print("predictedArray[predicted][actual]")
finalGen = trainer.get_current_generation()
for finalNetwork in finalGen:
    stats = finalNetwork.get_stats(statsInputs)
    print(stats[0])
    print(stats[1])
    print("")
