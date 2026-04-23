import random

class RandomAgent:
    def __init__(self, action_space=2):
        
        self.action_space = action_space

    def get_action(self, state, is_training=True):
        return random.randint(0, self.action_space - 1)
        
    def update(self, *args, **kwargs):
        
        pass
