from src.utils import *
from numpy import *


class DataPiece:
    def __init__(self, network_input, ideal_output):
        self.network_input = network_input
        self.ideal_output = ideal_output


class CategoricalDataPiece(DataPiece):
    def __init__(self, network_input, ideal_output_index, total_outputs):
        data = empty_array(total_outputs, 1)
        data[ideal_output_index][0] = 1.0
        super(CategoricalDataPiece, self).__init__(network_input, Matrix(data).reshape(len(data), len(data[0])))
        self.ideal_output_index = ideal_output_index


class CostFunction:
    def __init__(self):
        pass

    def cost(self, network, inp):
        return mean

    def copy(self):
        return type(self)()


class BackpropagatableCostFunction(CostFunction):
    def __init__(self):
        super(BackpropagatableCostFunction, self).__init__()

    def individual_gradient_descent(self, network, inp):
        pass

    def gradient_descent(self, network, inps, eta=0.5):
        mean = self.individual_gradient_descent(network, inps[0])
        #print("1 done")
        for index in range(1,len(inps)):
            grad_desc = self.individual_gradient_descent(network, inps[index])
            #print(str(index + 1), "done")
            for matrix_index in range(len(mean[0])):
                mean[0][matrix_index] += grad_desc[0][matrix_index]
                mean[1][matrix_index] += grad_desc[1][matrix_index]
        scale = -eta / len(inps)
        for index in range(len(mean[0])):
            mean[0][index] *= scale
            mean[1][index] *= scale
        return mean


class SquareOfDifference(BackpropagatableCostFunction):
    def __init__(self):
        super(SquareOfDifference, self).__init__()

    def cost(self, network, inp):
        full_res_nd = network.evaluate(inp[0].network_input).A
        full_ideal_nd = inp[0].ideal_output.A
        for index in range(1, len(inp)):
            full_res_nd = append(full_res_nd, inp[index].network_input)
            full_ideal_nd = append(full_ideal_nd, inp[index].ideal_output)
        diff = matrix(full_res_nd) - matrix(full_ideal_nd)
        return (diff.T * diff).item((0,0))

    def individual_gradient_descent(self, network, inp):
        weights = network.get_weights()
        biases = network.get_biases()
        nonsigmoid_activations = network.evaluate_nonsigmoid_activations(inp.network_input)
        layers = network.get_layers()
        activations = network.evaluate_activations_with_nonsigmoid(nonsigmoid_activations)
        weight_deris, bias_deris, activation_deris = [], [], []
        for index in range(len(weights)):
            weight_deris.append(matrix(zeros((weights[index].shape[0], weights[index].shape[1]))))
            bias_deris.append(matrix(zeros((biases[index].shape[0], 1))))
            activation_deris.append(matrix(zeros((activations[index].shape[0], 1))))

        for row in range(layers[-1]):
            activation_deris[-1].put(row, 2 * (activations[-1].item((row, 0)) - inp.ideal_output.item((row, 0))))
        for layer in range(len(activations) - 1, -1, -1):
            for row in range(layers[layer + 1]):
                common_mult = sigmoid_derivative(nonsigmoid_activations[layer].item((row, 0)))\
                              * activation_deris[layer].item((row, 0))
                bias_deris[layer] = common_mult
                for col in range(layers[layer]):
                    if layer != 0:
                        weight_deris[layer].put(row * weight_deris[layer].shape[1] + col,
                                                activations[layer - 1].item((col, 0)) * common_mult)
                        activation_deris[layer - 1].put(col, activation_deris[layer - 1].item((col, 0))
                                                    + weights[layer].item((row, col)) * common_mult)
                    else:
                        weight_deris[layer].put(row * weight_deris[layer].shape[1] + col,
                                                inp.network_input.item((col, 0)) * common_mult)

        return weight_deris, bias_deris
