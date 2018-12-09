from math import *
from numpy import *


def empty_array(rows, columns):
    return matrix(zeros((rows, columns))).tolist()


def sigmoid(x):
    return 1.0 / (1.0 + exp(-x))


def sigmoid_derivative(x):
    s = sigmoid(x)
    return s.transpose() * (1 - s)


def random_matrix(rows, columns, max_val=1):
    return randn((rows, columns)) * max_val
