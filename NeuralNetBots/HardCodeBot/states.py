import math
from NeuralNetBots.HardCodeBot.hardcodebot import *


class StatesHandler:
    def __init__(self):
        # Example list of state functions
        self.state = {
            'atba': {'active': False, 'call': ATBA.atba, 'finishcheck': ATBA.atbafinished},
            'driveforward': {'active': False, 'call': DriveForward.driveforward,
                             'finishcheck': DriveForward.driveforwardfinished},
            '0': False,
            '1': False,
            '2': False,
            '3': False
        }

    def choosestate(self, ball, me, others, info):
        # Choose the state via conditions, wipe states, apply state
        # Having a playtype selector might be useful (Shot, Defend, Aerial)
        # If i'm not the fastest to the ball, determine offensive or defensive

        # Temporary Test Code:
        if self.state['atba']['active']:
            nextstate = "driveforward"
        else:
            nextstate = "atba"
        # End Test Code

        self.statesclear()
        self.state[nextstate]['call'] = True

    def execute(self, state, ball, me, others, info):
        self.state[state]['finished'](ball, me, others, info)
        if self.state[state] and self.stateavailability[state](ball, me, others, info):
            return self.statecalls[state](ball, me, others, info)
        else:
            self.choosestate(ball, me, others, info)

    def carfieldposition(self, car):
        '''
        Definition of Positions on the field:
        Looking from above, coordinate plane on field, (X team) goal at pos y and (Y team) goal at neg. y:
        On ground: Defensive: 0, Offensive: 1
        Lower Wall curves: Back: 2, Side Defensive: 3, Side Offensive: 4, Front: 5
        Walls: Back Defensive: 6, Side Defensive: 7, Side Offensive: 8, Front Offensive: 9
        Ceilings, Upper Corner & Wall Curves: Defensive: 10, Offensive: 11
        Aerials: Defensive Low: 12, Defensive High: 13, Offensive Low: 14, Offensive High: 15
        In-net: Defensive: 16, Offensive: 17
        '''
        # In net
        if abs(car['location']['y']) >= 5120.0:
            if self.ondefensive(me):
                return 19
            else:
                return 20
        # On the ground
        elif car['wheelcontact'] and abs(car['rotation']['pitch']) <= math.pi/6.0 and \
                abs(car['rotation']['yaw']) <= math.pi/6.0 and abs(car['rotation']['roll']) <= math.pi/6.0:
            if self.ondefensive(car):
                return 0
            else:
                return 1
        # On the lower wall curves
        elif car['wheelcontact'] and car['location']['z'] <= 40.0:
            if self.ondefensive(car):
                if self.backwall(car):
                    return 2
                else:
                    return 3
            else:
                if self.backwall(car):
                    return 4
                else:
                    return 5
        # On the wall
        elif car['wheelcontact'] and car['location']['z'] <= 2000.0:
            if self.ondefensive(car):
                if self.backwall(car):
                    return 6
                else:
                    return 7
            else:
                if self.backwall(car):
                    return 8
                else:
                    return 9
        # Ceilings
        elif car['wheelcontact']:
            if self.ondefensive(car):
                return 10
            else:
                return 11
        # Aerial
        else:
            if self.ondefensive(car):
                if car['location']['z'] <= 1000.0:
                    return 12
                else:
                    return 13
            else:
                if car['location']['z'] <= 1000.0:
                    return 14
                else:
                    return 15

    def ballcondition(self, ball):
        '''
        Definition of ball conditions on the field:
        Defensive Rolling on Ground: 0
        Offensive Rolling on Ground: 1
        Defensive Bouncing near ground: 2
        Offensive Bouncing near ground: 3
        Defensive Medium bouncing: 4
        Offensive Medium bouncing: 5
        Defensive High Bouncing: 6
        Offensive High Bouncing: 7
        Defensive On Side-wall: 8
        Offensive On Side-wall: 9
        On Back wall: 10
        On Front wall: 11
        General In-Air: 12
        '''
        # Check ball location and velocity:
        # Side Walls
        if abs(ball['location']['x']) > 3800.0 and abs(ball['velocity']['x']) < 150.0:
            if self.ondefensive(ball['location']):
                return 8
            else:
                return 9
        # End Walls
        elif abs(ball['location']['y']) > 4850.0 and abs(ball['velocity']['y']) < 150.0:
            if self.ondefensive(ball['location']):
                return 10
            else:
                return 11
        # Not On A Wall
        elif abs(ball['location']['x']) < 3800.0 and abs(ball['location']['y']) < 4850:
            if ball['location']['z'] <= 100.0 and -16.7 <= ball['velocity']['z'] <= 10.0:
                if self.ondefensive(ball['location']):
                    return 0
                else:
                    return 1
            elif ball['location']['z'] <= 300.0 and -167.0 <= ball['velocity']['z'] <= 100.0:
                if self.ondefensive(ball['location']):
                    return 2
                else:
                    return 3
            elif ball['location']['z'] <= 600.0 and -670.0 <= ball['velocity']['z'] <= 400.0:
                if self.ondefensive(ball['location']):
                    return 4
                else:
                    return 5
            else:
                if self.ondefensive(ball['location']):
                    return 6
                else:
                    return 7
        else:
            return 12

    @staticmethod
    def ondefensive(location):
        if location['location']['y'] >= 0.0:
            return True
        else:
            return False

    @staticmethod
    def backwall(car):
        if car['location']['y'] >= 5020.0:
            return True
        else:
            return False

    @staticmethod
    def controllerreturn(throttle=0.0, steer=0.0, pitch=0.0, yaw=0.0, roll=0.0, jump=False, boost=False, handbrake=False):
        return {
            'throttle': throttle,
            'steer': steer,
            'pitch': pitch,
            'yaw': yaw,
            'roll': roll,
            'jump': jump,
            'boost': boost,
            'handbrake': handbrake
        }

    def statesclear(self):
        for i in self.state:
            self.state[i]['active'] = False


class States:

    @staticmethod
    def ground():
        return StatesHandler.controllerreturn()

    @staticmethod
    def angle_2d(self, carvector, ballvector):
        return math.atan(carvector['y'] / carvector['x']) - math.asin(
            self.relativepos_2d(carvector, ballvector)['y'] / self.relativepos_2d(carvector, ballvector)['x'])

    @staticmethod
    def relativepos_2d(origin, location):
        return {'x': location['x'] + origin['x'], 'y': location['y'] + location['y']}


class ATBA(States):

    carconditions = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17]
    ballconditions = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]

    def atba(self, ball, me, others, info):
        towardsball = self.angle_2d(me['rotation'], ball['location'])
        steer = towardsball/math.pi/2
        return StatesHandler.controllerreturn(False, 100, steer)

    @staticmethod
    def atbafinished(ball, me, others, info):
        if info['player'] == HardCodeBot.myusername:
            return True
        else:
            return False


class DriveForward(States):

    @staticmethod
    def driveforward(me):
        pitch = 0
        yaw = 0
        roll = 0
        if me['rotation']['roll'] != 0:
            roll = -1 * me['rotation']['roll']
            if abs(roll) > 1:
                roll = abs(roll)/roll

        if me['rotation']['yaw'] != 0 or me['rotation']['yaw'] != math.pi:
            if abs(me['rotation']['yaw'] - math.pi) <= abs(me['rotation']['yaw']):
                yaw = -1 * (me['rotation']['yaw'] - math.pi)
                if abs(yaw) > 1:
                    yaw = abs(yaw)/yaw
            else:
                yaw = -1 * me['rotation']['yaw']
                if abs(yaw) > 1:
                    yaw = abs(yaw)/yaw
        if me['rotationd']['pitch'] != 0:
            pitch = -1 * me['rotation']['pitch']
            if abs(pitch) > 1:
                pitch = abs(pitch)/pitch
        throttle = 1
        boost = True
        return StatesHandler.controllerreturn(throttle, 0, pitch, yaw, roll, False, boost, False)

    @staticmethod
    def driveforwardavailable():
        return True

    @staticmethod
    def driveforwardfinished(ball, me, others, info):
        if me['location']['y'] < 0:
            return True
        else:
            return False
