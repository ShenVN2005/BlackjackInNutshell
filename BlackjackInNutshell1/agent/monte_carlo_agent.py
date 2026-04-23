import numpy as np
from collections import defaultdict

class MonteCarloAgent:
    def __init__(self, action_space=3, epsilon=0.1):
        self.action_space = action_space
        self.epsilon = epsilon
        
        self.q_table = defaultdict(lambda: np.zeros(self.action_space))
        
        self.returns = defaultdict(list)
        
    def get_action(self, state, is_training=True):
        if is_training and np.random.rand() < self.epsilon:
            return np.random.randint(self.action_space)
        return np.argmax(self.q_table[state])
        
    def update(self, episode, final_reward):
        
        visited_state_actions = set()
        
        for state, action in episode:
            
            if (state, action) not in visited_state_actions:
                visited_state_actions.add((state, action))
                self.returns[(state, action)].append(final_reward)
                
                self.q_table[state][action] = np.mean(self.returns[(state, action)])
