from src.utils import *
from numpy import matrix


class NeuralNetwork:
    def __init__(self, layers):
        if len(layers) < 2:
            raise Exception("Need at least two layers to create a neural network")

        self._layers = layers
        self._weights = []
        self._biases = []
        for layer in range(len(layers) - 1):
            self._weights.append(random_matrix(layers[layer + 1], layers[layer]))
            self._biases.append(random_matrix(layers[layer + 1], 1))
        self._costFunction = None

    def get_layers(self):
        return self._layers.copy()

    def get_input_nodes(self):
        return self._layers[0]

    def get_output_nodes(self):
        return self._layers[-1]

    def evaluate_nonsigmoid_activations(self, inp):
        nodes = inp.copy()
        ret = []
        if nodes.shape[0] != self.get_input_nodes():
            raise Exception("Input data does not match the number of input nodes")
        for layer in range(len(self._layers) - 1):
            nodes = self._weights[layer] * nodes + self._biases[layer]
            ret.append(nodes.copy())
            nodes = sigmoid(nodes)
        return ret

    def evaluate_activations_with_nonsigmoid(self, nonsigmoid):
        ret = []
        for activation in nonsigmoid:
            ret.append(sigmoid(activation))
        return ret

    def evaluate_activations(self, inp):
        return self.evaluate_activations_with_nonsigmoid(self.evaluate_nonsigmoid_activations(inp))

    def evaluate(self, inp):
        return self.evaluate_activations(inp)[-1]

    def get_stats(self, cat_dps):
        right_wrong = {"correct": 0, "incorrect": 0}
        prediction_array = empty_array(cat_dps[0].ideal_output.shape[0], cat_dps[0].ideal_output.shape[0])
        for dp in cat_dps:
            res = self.evaluate(dp.network_input)
            maxIndex = res.argmax()
            ##            print("maxIndex", maxIndex, "index", index)
            ##            print(type(prediction_array), type(prediction_array[0]), type(prediction_array[0][0]))
            ##            print(type(catDps[0]))
            prediction_array[maxIndex][dp.ideal_output_index] += 1
            if dp.ideal_output_index == maxIndex:
                right_wrong["correct"] += 1
            else:
                right_wrong["incorrect"] += 1
        return right_wrong, matrix(prediction_array)

    def get_weights(self):
        weights = []
        for weight in self._weights:
            weights.append(weight.copy())
        return weights

    def get_biases(self):
        biases = []
        for bias in self._biases:
            biases.append(bias.copy())
        return biases

    def set_weights(self, weights):
        if not len(weights) == len(self._layers) - 1:
            raise Exception("Network needs " + str(len(self._layers) - 1) + " weight matrices")
        if not self._layers[0] == weights[0].shape[1]:
            raise Exception(
                "Number of columns in weight matrix 0 must equal the amount of nodes in the input layer (" + str(
                    self._layers[0]) + ")")
        for index in range(len(weights)):
            if not weights[index].shape[0] == self._layers[index + 1]:
                raise Exception(
                    "Number of rows in matrix " + str(index) + " must equal the amount of nodes in layer " + str(
                        index + 1))
            if index > 0 and not weights[index - 1].shape[0] == weights[index].shape[1]:
                raise Exception(
                    "Number of rows in matrix " + str(index - 1) + " must equal the nymber of columns in matrix " + str(
                        index))
        self._weights = weights

    def set_biases(self, biases):
        if not len(biases) == len(self._layers) - 1:
            raise Exception("Network needs " + str(len(self._layers) - 1) + " bias matrices")
        for index in range(len(biases)):
            if not biases[index].shape[0] == self._layers[index + 1]:
                raise Exception(
                    "Number of rows in bias matrix " + str(index) + " must equal the number of nodes in layer " + str(
                        index + 1) + " (" + str(self._layer[index + 1]) + ")")
            if not biases[index].shape[1] == 1:
                raise Exception("Number of columns in bias matrix " + str(index) + " must equal 1")
        self._biases = biases


def create_neural_network(weights, biases):
    if len(weights) != len(biases):
        raise Exception("Number of weight matrices must equal the number of bias matrices")
    layers = [weights[0].shape[1]]
    for weight in weights:
        layers.append(weight.shape[0])
    network = NeuralNetwork(layers)
    network.set_weights(weights)
    network.set_biases(biases)
    return network
