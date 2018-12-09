from random import *
from src.utils import *
from src.neuralnetwork.neuralnetwork import *
from src.neuralnetwork.costfunction import *
from math import *
from numpy import *


class Trainer:
    def __init__(self, initial, cost_function):
        self._generation = [initial]
        self._cost_function = cost_function

    def train_next_generation(self, cost_inputs):
        pass

    def get_current_generation(self):
        return self._generation


class BackpropagateTrainer(Trainer):
    def __init__(self, initial, cost_function):
        super(BackpropagateTrainer, self).__init__(initial, cost_function)

    def train_next_generation(self, cost_inputs):
        network = self.get_current_generation()[0]
        grad_desc = self._cost_function.gradient_descent(network, cost_inputs)
        weights, biases = network.get_weights(), network.get_biases()
        for index in range(len(grad_desc)):
            weights[index] += grad_desc[0][index]
            biases[index] += grad_desc[1][index]
        self._generation[0] = create_neural_network(weights, biases)


class EvolutionTrainer(Trainer):
    def __init__(self, generation_size, number_of_children, initial_max_step, max_step_scalar,
                 initial, cost_function):
        super(EvolutionTrainer, self).__init__(initial, cost_function)
        self._generation_size = generation_size
        self._number_of_children = number_of_children
        self._max_step = initial_max_step
        self._max_step_scalar = max_step_scalar

    def train_next_generation(self, cost_inputs):
        rand = Random()
        current_gen = self.get_current_generation()
        next_gen = []
        for parent in current_gen:
            weights = parent.get_weights()
            biases = parent.get_biases()
            for child in range(self._number_of_children):
                new_weights, new_biases = [], []
                for index in range(len(weights)):
                    random_weight = self._max_step * random_matrix(weights[index].shape[0], weights[index].shape[1])
                    subtract_mat = matrix(range(weights[index].shape[0] * weights[index].shape[1])).reshape((
                        weights[index].shape[0], weights[index].shape[1]))
                    subtract_mat.fill(self._max_step)
                    random_weight -= subtract_mat
                    new_weights.append(random_weight)

                    random_bias = self._max_step * random_matrix(biases[index].shape[0], 1)
                    random_bias -= matrix([self._max_step] * biases[index].shape[0]).reshape(biases[index].shape[0], 1)
                    new_biases.append(random_bias)
                next_gen.append(create_neural_network(new_weights, new_biases))

        costs = {}
        max_min = float("-inf")
        max_min_index = -1
        for index in range(len(next_gen)):
            cost = self._cost_function.cost(next_gen[index], cost_inputs)
            if len(costs) >= self._generation_size and cost < max_min:
                costs[index] = cost
                costs.pop(max_min_index)

                max_min = float("-inf")
                for entry in iter(costs.items()):
                    if entry[1] > max_min:
                        max_min = entry[1]
                        max_min_index = entry[0]
            elif len(costs) < self._generation_size:
                costs[index] = cost
                if len(costs) == self._generation_size:
                    for entry in iter(costs.items()):
                        if entry[1] > max_min:
                            max_min = entry[1]
                            max_min_index = entry[0]
        print("got costs")

        survivors = []
        for entry in iter(costs.items()):
            survivors.append(next_gen[entry[0]])
        self._generation = survivors

        self._max_step *= self._max_step_scalar
        # print("Determined survivors")


def train(trainer, cost_inputs, num_times=1):
    last_percent = 0
    for run in range(num_times):
        if type(cost_inputs[0]) is list:
            for index in range(len(cost_inputs)):
                trainer.train_next_generation(cost_inputs[index])
                percent = (run * len(cost_inputs) + index + 1.0) / (len(cost_inputs) * num_times) * 100
                if percent >= last_percent + 1:
                    last_percent = floor(percent)
                    print(str(last_percent) + "%")
        else:
            trainer.train_next_generation(cost_inputs)
            percent = (run + 1.0) / num_times * 100
            if percent >= last_percent + 1:
                last_percent = floor(percent)
                print(str(last_percent) + "%")
