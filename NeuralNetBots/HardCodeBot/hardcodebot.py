import math

from rlbot.agents.base_agent import BaseAgent, SimpleControllerState
from rlbot.utils.structures.game_data_struct import GameTickPacket
from numpy import *
from NeuralNetBots.HardCodeBot.States import StatesHandler, CurrentState


class HardCodeBot(BaseAgent):

    def initialize_agent(self):
        self.controller_state = SimpleControllerState()
        self.last_touch = {'name': "", 'time': 0.0, 'timesince': 0.0}
        self.myusername = ""

    def get_output(self, game: GameTickPacket, rigidbody: BaseAgent.get_rigid_body_tick()) -> SimpleControllerState:
        state = "ground state"
        preprocess = self.preprocess(game, rigidbody)
        for i in StatesHandler.state:
            if StatesHandler.state[i]:
                state = StatesHandler.state[i]
        output = StatesHandler.execute(HardCodeBot.States.StateHandler, state, preprocess['ball'],
                                       preprocess['me'], preprocess['others'], preprocess['info'])
        self.controllerstate.throttle = output['throttle']
        self.controllerstate.steer = output['steer']
        self.controllerstate.pitch = output['pitch']
        self.controllerstate.yaw = output['yaw']
        self.controllerstate.roll = output['roll']
        self.controllerstate.jump = output['jump']
        self.controllerstate.boost = output['boost']
        self.controllerstate.handbrake = output['handbrake']
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


class UtilFunctions:
    def distance(self, coords1, coords2):
        distance = self.magnitude({'x': abs(coords1['x']-coords2['x']),
                                   'y': abs(coords1['y']-coords2['y']),
                                   'z': abs(coords1['z']-coords2['z'])})
        return distance

    def towardsball(self, balllocation, carlocation, carrotation, carvelocity):
        bl = balllocation
        cl = carlocation
        r = carrotation
        v = carvelocity
        balltocarvector = {'x': cl['x'] - bl['x'], 'y': cl['y'] - bl['y'], 'z': cl['z'] - bl['z']}
        if self.hemispherecheck(balltocarvector, r) or self.hemispherecheck(balltocarvector, v):
            return True
        else:
            return False

    @staticmethod
    def magnitude(vector):
        x = math.sqrt(pow(vector['x'], 2) + pow(vector['y'], 2) + pow(vector['z'], 2))
        return x

    @staticmethod
    def dotproduct(vector1, vector2):
        x = vector1['x'] * vector2['x'] + vector1['y'] * vector2['y'] + vector1['z'] * vector2['z']
        return x

    def hemispherecheck(self, planevector, checkvector):
        x = math.acos(
            self.dotproduct(planevector, checkvector) / (self.magnitude(planevector) * self.magnitude(checkvector)))
        if x <= math.pi / 2:
            return True
        else:
            return False

    def mintimetoball(self, me, others):
        '''
        for i in range(len(others)):
            if self.touchingground(i, game):
                # on the ground
                # Velocity +/- 500 uu/s for flip
                pass
            elif self.hasdoublejump(i, game):
                # has a double jump
                pass
            else:
                # in midair, no flip
                pass
        '''
        pass

    def bounce(self):
        '''
        Ball Bounce Prediction Code:
        ball_prediction = self.get_ball_prediction_struct()

        if ball_prediction is not None:
            for i in range(0, ball_prediction.num_slices):
                prediction_slice = ball_prediction.slices[i]
                location = prediction_slice.physics.location
                self.logger.info("At time {}, the ball will be at ({}, {}, {})"
                                 .format(prediction_slice.game_seconds, location.x, location.y, location.z))
        '''
        pass

    def hitground(self, ball):
        pass

    @staticmethod
    def touchingground(i, game):
        if game.game_cars[i].has_wheel_contact and game.game_cars[i].physics.location.z <= 80:
            return True
        else:
            return False

    @staticmethod
    def hasdoublejump(i, game):
        if not game.game_cars[i].double_jumped:
            return True
        else:
            return False

    @staticmethod
    def quaterniontoeuler(q):
        yaw = math.atan2(2*(q['x']*q['y'] + q['z']*q['w']), 1-2*(pow(q['y'], 2) + pow(q['z'], 2)))
        pitch = math.asin(2*(q['x']*q['z']) - q['w']*q['y'])
        roll = math.atan2(2*(q['x']*q['w'] + q['y']*q['z']), 1-2*(pow(q['z'], 2) + pow(q['w'], 2)))
        return{
            'x': yaw,
            'y': pitch,
            'z': roll
        }

    def closestcar(self, me, others, ball):
        medist = self.distance(me['location'], ball['location'])
        othersdist = [len(others)]
        closest = -1
        for i in range(len(others)):
            othersdist[i] = self.distance(others[i]['location'], ball['location'])
            if othersdist[i] < medist:
                closest = i
        return closest


'''class Renderer(BaseAgent):

    @staticmethod
    def drawcurve(start, end, length, rotation):
        # Draws a line from a to b of arc length c with rotation d radians when viewed from a looking at b.
        # Done by using 10 small line segments connected by intermediate points
        starttoend = UtilFunctions.distance(start, end)
        if length >= starttoend:
            dist = []
        else:
            pass
'''
