import math
import random

from rlbot.agents.base_agent import BaseAgent, SimpleControllerState
from rlbot.utils.structures.game_data_struct import GameTickPacket
from numpy import *


class HardCodeBot(BaseAgent):
    
    def initialize_agent(self):
        self.controller_state = SimpleControllerState()

    def get_output(self, game: GameTickPacket) -> SimpleControllerState:
        self.preprocess(game)
        return self.controller_state

    
    def preprocess(self,game):
        car = game.game_cars[self.index]
        mylocationdata = {"x": car.physics.location.x, "y": car.physics.location.y, "z": car.physics.location.z}
        myvelocitydata = {"x": car.physics.velocity.x, "y": car.physics.velocity.y, "z": car.physics.velocity.z}
        myrotationdata = {"x": car.physics.rotation.pitch, "y": car.physics.rotation.yaw, "z": car.physics.rotation.roll}
        myrvelocitydata = {"x": car.physics.angular_velocity.x, "y": car.physics.angular_velocity.y, "z": car.physics.angular_velocity.z}
        myboost = car.boost

        ball = game.game_ball.physics
        balllocationdata = {"x": ball.location.x, "y": ball.location.y, "z": ball.location.z}
        ballvelocitydata = {"x": ball.velocity.x, "y": ball.velocity.y, "z": ball.velocity.z}
        ballrotationdata = {"x": ball.rotation.pitch, "y": ball.rotation.yaw, "z": ball.rotation.roll}
        ballrvelocitydata = {"x": ball.angular_velocity.x, "y": ball.angular_velocity.y, "z": ball.angular_velocity.z}

        other = []
        nodes = []
        for i in range(8):
            if i != self.index:
                car = game.game_cars[i]
                other.append({"team": car.team,
                    "locationdata": {"x": car.physics.location.x, "y": car.physics.location.y, "z": car.physics.location.z},
                    "velocitydata": {"x": car.physics.velocity.x, "y": car.physics.velocity.y, "z": car.physics.velocity.z},
                    "rotationdata": {"x": car.physics.rotation.pitch, "y": car.physics.rotation.yaw, "z": car.physics.rotation.roll},
                    "rvelocitydata": {"x": car.physics.angular_velocity.x, "y": car.physics.angular_velocity.y, "z": car.physics.angular_velocity.z},
                    "boost":0})