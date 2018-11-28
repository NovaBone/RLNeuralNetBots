import math
import random

from rlbot.agents.base_agent import BaseAgent, SimpleControllerState
from rlbot.utils.structures.game_data_struct import GameTickPacket
from numpy import *


class NeuralBot(BaseAgent):
    
    def initialize_agent(self):
        self.controller_state = SimpleControllerState()

    def get_output(self, game: GameTickPacket) -> SimpleControllerState:
        self.preprocess(game)
        '''
        Netoutput[] has 8 values:
        self.controllerstate.throttle = outputtofloat(netoutput[0])
        self.controllerstate.steer = outputtofloat(netoutput[1])
        self.controllerstate.pitch = outputtofloat(netoutput[2])
        self.controllerstate.yaw = outputtofloat(netoutput[3])
        self.controllerstate.roll = outputtofloat(netoutput[4])
        self.controllerstate.jump = outputtobool(netoutput[5])
        self.controllerstate.boost = outputtobool(netoutput[6])
        self.controllerstate.handbrake = outputtobool(netoutput[7])
        '''
        return self.controller_state

    
    def preprocess(self,game):
        car = game.game_cars[self.index]
        mylocationdata = {"x":car.physics.location.x, "y":car.physics.location.y, "z":car.physics.location.z}
        myvelocitydata = {"x":car.physics.velocity.x, "y":car.physics.velocity.y, "z":car.physics.velocity.z}
        myrotationdata = {"x":car.physics.rotation.pitch, "y":car.physics.rotation.yaw, "z":car.physics.rotation.roll}
        myrvelocitydata = {"x":car.physics.angular_velocity.x, "y":car.physics.angular_velocity.y, "z":car.physics.angular_velocity.z}
        myboost = car.boost

        ball = game.game_ball.physics
        balllocationdata = {"x":ball.location.x, "y":ball.location.y, "z":ball.location.z}
        ballvelocitydata = {"x":ball.velocity.x, "y":ball.velocity.y, "z":ball.velocity.z}
        ballrotationdata = {"x":ball.rotation.pitch, "y":ball.rotation.yaw, "z":ball.rotation.roll}
        ballrvelocitydata = {"x":ball.angular_velocity.x, "y":ball.angular_velocity.y, "z":ball.angular_velocity.z}

        other = []
        nodes = []
        for i in range(8):
            if i != self.index:
                car = game.game_cars[i]
                other.append({"team": car.team,
                    "locationdata": {"x": car.physics.location.x, "y": car.physics.location.y, "z": car.physics.location.z},
                    "velocitydata": {"x": car.physics.velocity.x, "y": car.physics.velocity.y, "z": car.physics.velocity.z},
                    "rotationdata": {"x":car.physics.rotation.pitch, "y": car.physics.rotation.yaw, "z": car.physics.rotation.roll},
                    "rvelocitydata": {"x":car.physics.angular_velocity.x, "y": car.physics.angular_velocity.y, "z": car.physics.angular_velocity.z},
                    "boost":0})
        nodes.append((mylocationdata["x"]+4096.0)/8192.0)
        nodes.append((mylocationdata["y"]+6500.0)/13000.0)
        nodes.append(mylocationdata["z"]/2044.0)
        nodes.append((myvelocitydata["x"]+2300.0)/4600.0)
        nodes.append((myvelocitydata["y"]+2300.0)/4600.0)
        nodes.append((myvelocitydata["z"]+2300.0)/4600.0)
        nodes.append((myrotationdata["x"]+3.5)/15)
        nodes.append((myrotationdata["y"]+3.5)/15)
        nodes.append((myrotationdata["z"]+3.5)/15)
        nodes.append((myrvelocitydata["x"]+5.5)/11)
        nodes.append((myrvelocitydata["y"]+5.5)/11)
        nodes.append((myrvelocitydata["z"]+5.5)/11)
        nodes.append(myboost/100)

        nodes.append((balllocationdata["x"]+4096.0)/8192.0)
        nodes.append((balllocationdata["y"]+6500.0)/13000.0)
        nodes.append(balllocationdata["z"]/2044.0)
        nodes.append((ballvelocitydata["x"]+6000.0)/12000.0)
        nodes.append((ballvelocitydata["y"]+6000.0)/12000.0)
        nodes.append((ballvelocitydata["z"]+6000.0)/12000.0)
        nodes.append((ballrotationdata["x"]+3.5)/14)
        nodes.append((ballrotationdata["y"]+3.5)/14)
        nodes.append((ballrotationdata["z"]+3.5)/14)
        nodes.append((ballrvelocitydata["x"]+6)/12)
        nodes.append((ballrvelocitydata["y"]+6)/12)
        nodes.append((ballrvelocitydata["z"]+6)/12)

        for i in range(7):
            nodes.append(other[i]["team"])
            nodes.append(other[i]["boost"])
            nodes.append((other[i]["locationdata"]["x"]+4096.0)/8192.0)
            nodes.append((other[i]["locationdata"]["y"]+6500.0)/13000.0)
            nodes.append(other[i]["locationdata"]["z"]/2044.0)
            nodes.append((other[i]["velocitydata"]["x"]+2300.0)/4600.0)
            nodes.append((other[i]["velocitydata"]["y"]+2300.0)/4600.0)
            nodes.append((other[i]["velocitydata"]["z"]+2300.0)/4600.0)
            nodes.append((other[i]["rotationdata"]["x"]+3.5)/15)
            nodes.append((other[i]["rotationdata"]["y"]+3.5)/15)
            nodes.append((other[i]["rotationdata"]["z"]+3.5)/15)
            nodes.append((other[i]["rvelocitydata"]["x"]+5.5)/11)
            nodes.append((other[i]["rvelocitydata"]["y"]+5.5)/11)
            nodes.append((other[i]["rvelocitydata"]["z"]+5.5)/11)

        nodes.append(game.game_info.game_time_remaining/300)
        nodes.append(game.game_info.goals/500)
        nodes.append(game.game_info.ownGoals/500)

    def outputtofloat(n):return (n*2)-n

    def outputtobool(n):
        if 1 >= n >= 0.5:
            return True
        elif 0.5 > n >= 0:
            return False
        else:
            return False

class NeuralStructure:
    def __init__(self):
        pi=math.pi
        neuralstructure = [126, 32, 32, 16, 16, 16, 8]
        neuralweightmatrix = []
        for i in range(len(neuralstructure)-1):
            for j in range(neuralstructure[i]):
                neuralweightmatrix[i].append()
                for k in range(neuralstructure[i+1]):
                    neuralweightmatrix[i][j].append(NeuralBot.outputtofloat(random()))
        neuralbiasmatrix = []
        for i in range(len(neuralstructure)-1):
            for j in range(neuralstructure[i+1]):
                neuralbiasmatrix[i].append(NeuralBot.outputtofloat(random()))
        

    def process(self,matrix):
        pass

'''
class MatrixFunctionsPlus:
    def __init__(self):
        pass

    def matrixmultiply(self,matrix1,matrix2):
        [[1,3,5],[2,4,6]]
        #check if both are 2 dimensions and compatible dimensions
        pass
    def dimensions(self,matrix1):
        if not is2D(matrix1):
            return {
            'error': True,
            'isSquare':False,
            'width':0,
            'height':0
        }
        a1 = len(matrix1)
        b1 = len(matrix1[0])
        rect = True
        for i in range(a1):
            if len(matrix1[i]) == b1:
                pass
            else:
                rect=False
        return {
            'error': False,
            'isSquare':rect,
            'width':a1,
            'height':b1
        }

    def is2D(self, matrix):
        for i in range(matrix):
            try:
                for j in range(matrix[i]):
                    try:
                        for k in range(matrix[i][j]):
                            if k > 1:
                                #3+ Dimensions
                                return False
                            else:
                                #2 Dimensions
                                return True
                    except:
                        #1 Dimension
                        return False
            except:
                #0 Dimensions
                return False
    def sigmoid(self,num,modifier=1):return modifier * (1/(1+exp(-1*num)))
'''

'''
    Fitness Functions:
    1. Distance to ball
    2. Distance to ball x Time Taken
    3. Distance from Ball to Point
    4. Distance from Ball to Point x Time Taken
    5. Distance from Ground
    6. Distance from Ground x Time Successful
    7. Human Player No-Touch x Time Successful
    8. Demolitions on Stationary x Time Taken
    9. Demolitions on Player x Time Taken
    10. Goals > OwnGoals [Offensive Tendencies]
    11. OwnGoals > Goals [Defensive Tendencies]
'''