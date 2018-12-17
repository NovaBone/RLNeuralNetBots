import math
import random

from rlbot.agents.base_agent import BaseAgent, SimpleControllerState
from rlbot.utils.structures.game_data_struct import GameTickPacket
from numpy import *


class NeuralBot(BaseAgent):
    
    def initialize_agent(self):
        self.controller_state = SimpleControllerState()
        self.myusername = ""
        self.nodes = []

    def get_output(self, game: GameTickPacket, body: BaseAgent.get_rigid_body_tick()) -> SimpleControllerState:
        gamedata = self.preprocess(game, body)
        createnodes(gamedata)
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

    def preprocess(self, game, body):
        car = game.game_cars[self.index]
        mycar = body.players[self.index]
        wheelcontact = False
        if car.has_wheel_contact:
            wheelcontact = True
        doublejumped = True
        if not car.double_jumped:
            doublejumped = False
        mylocationdata = {"x": mycar.state.location.x, "y": mycar.state.location.y, "z": mycar.state.location.z}
        myvelocitydata = {"x": mycar.state.velocity.x, "y": mycar.state.velocity.y, "z": mycar.state.velocity.z}
        myrotation = UtilFunctions.quaterniontoeuler(mycar.state.rotation)
        myrotationdata = {"x": myrotation['pitch'], "y": myrotation['yaw'],
                          "z": myrotation['roll']}
        myrvelocitydata = {"x": mycar.state.angular_velocity.x, "y": mycar.state.angular_velocity.y,
                           "z": mycar.state.angular_velocity.z}
        myboost = car.boost
        mystats = {'locationdata': mylocationdata, 'velocitydata': myvelocitydata, 'rotationdata': myrotationdata,
                   'rvelocitydata': myrvelocitydata, 'boost': myboost, 'doublejumped': doublejumped,
                   'wheelcontact': wheelcontact}

        ball = body.ball
        balllocationdata = {"x": ball.location.x, "y": ball.location.y, "z": ball.location.z}
        ballvelocitydata = {"x": ball.velocity.x, "y": ball.velocity.y, "z": ball.velocity.z}
        rotation = UtilFunctions.quaterniontoeuler(ball.rotation)
        ballrotationdata = {"x": rotation['pitch'], "y": rotation['yaw'], "z": rotation['roll']}
        ballrvelocitydata = {"x": ball.angular_velocity.x, "y": ball.angular_velocity.y, "z": ball.angular_velocity.z}
        ballstats = {'location': balllocationdata, 'velocity': ballvelocitydata,
                     'rotation': ballrotationdata, 'rvelocity': ballrvelocitydata}

        otherstats = []
        for i in range(8):
            if i != self.index:
                car = game.game_cars[i]
                rigid = body.players[i]
                wheelcontact = False
                if car.has_wheel_contact:
                    wheelcontact = True
                doublejumped = True
                if not car.double_jumped:
                    doublejumped = False
                teammate = False
                if car.team == game.game_cars[self.index].team:
                    teammate = True
                rotation = UtilFunctions.quaterniontoeuler(rigid.state.rotation)
                otherstats.append({"teammate": teammate,
                                   "location": {"x": rigid.state.location.x,
                                                    "y": rigid.state.location.y,
                                                    "z": rigid.state.location.z},
                                   "velocity": {"x": rigid.state.velocity.x,
                                                    "y": rigid.state.velocity.y,
                                                    "z": rigid.state.velocity.z},
                                   "rotation": {"x": rotation['pitch'],
                                                    "y": rotation['yaw'],
                                                    "z": rotation['roll']},
                                   "rvelocity": {"x": rigid.state.angular_velocity.x,
                                                     "y": rigid.state.angular_velocity.y,
                                                     "z": rigid.state.angular_velocity.z},
                                   "boost": 0,
                                   "doublejumped": doublejumped,
                                   "wheelcontact": wheelcontact
                                   })
        for i in range(len(game.game_cars)):
            if i == self.index:
                self.myusername = game.game_cars[i]['name']
        info = game.game_ball.latest_touch
        touchinfo = {
            'player': info.player_name,
            'time': info.time_seconds
        }
        if touchinfo['player'] != self.last_touch['name']:
            self.last_touch['name'] = touchinfo['player']
            self.last_touch['time'] = touchinfo['time']
            self.last_touch['timesince'] = 0.0
        else:
            self.last_touch['timesince'] = game.game_info.seconds_elapsed - self.last_touch['time']
        return {
            'me': mystats,
            'ball': ballstats,
            'others': otherstats,
            'touchinfo': touchinfo
        }

    def createnodes(self, gamedata):
        for i in gamedata:
            if type(gamedata[i]) is dict:
                for j in gamedata:
                    if type(gamedata[i][j]) is dict:
                        for k in gamedata:
                            if type(gamedata[i][j][k]) is dict:
                                for l in gamedata:
                                    self.nodes.append(gamedata[i][j][k][l])
                            else:
                                self.nodes.append(gamedata[i][j][k])
                    else:
                        self.nodes.append(gamedata[i][j])
            else:
                self.nodes.append(gamedata[i])

    @staticmethod
    def outputtofloat(n):return (n*2)-n

    @staticmethod
    def outputtobool(n):
        if 1 >= n >= 0.5:
            return True
        elif 0.5 > n >= 0:
            return False
        else:
            return False

    @staticmethod
    def quaterniontoeuler(q):
        yaw = math.atan2(2 * (q['x'] * q['y'] + q['z'] * q['w']), 1 - 2 * (pow(q['y'], 2) + pow(q['z'], 2)))
        pitch = math.asin(2 * (q['x'] * q['z']) - q['w'] * q['y'])
        roll = math.atan2(2 * (q['x'] * q['w'] + q['y'] * q['z']), 1 - 2 * (pow(q['z'], 2) + pow(q['w'], 2)))
        return {
            'x': yaw,
            'y': pitch,
            'z': roll
        }

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