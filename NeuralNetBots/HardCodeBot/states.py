class StatesHandler:

    def choosestate(self, ball, me, others):
        # Example list of state functions
        self.statelist = {
            'dribble': self.atba(ball,me,others),
            'flick': "call()",
            'pass': "call()",
            '0': "call()",
            '1': "call()",
            '2': "call()",
            '3': "call()",
            '4': "call()",
            '5': "call()",
            '6': "call()",
            '7': "call()",
            '8': "call()",
            '9': "call()"
        }

    def execute(self, state):
        if '''state incomplete''':
            self.stateList[state]
        else:
            return {
                'Finished': True,
                'throttle': 0,
                'steer': 0,
                'pitch': 0,
                'yaw': 0,
                'roll': 0,
                'jump': 0,
                'boost': 0,
                'handbrake': 0
            }


class States:

    def atba(self,ball,me,others):
        pass
