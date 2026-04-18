import random

class RandomAgent:
    def __init__(self, action_space=2):
        # We limit the action scope to 0 (Stand) and 1 (Hit). 
        # Action space 2 specifically represents Surrender, which the agent refuses.
        self.action_space = action_space

    def get_action(self, state, is_training=True):
        return random.randint(0, self.action_space - 1)
        
    def update(self, *args, **kwargs):
        # Random agent doesn't learn
        pass
