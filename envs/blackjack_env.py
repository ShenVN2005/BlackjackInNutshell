import gymnasium as gym
from gymnasium import spaces
import random

def get_card_value(card_str):
    if card_str == "HIDDEN":
        return 0
    for s in ['Bich', 'Co', 'Ro', 'Tep']:
        if card_str.endswith(s):
            val_str = card_str[:-len(s)]
            break
    if val_str in ['J', 'Q', 'K']: return 10
    if val_str == 'A': return 11
    return int(val_str)

def score_hand(hand):
    values = [get_card_value(c) for c in hand if c != "HIDDEN"]
    score = sum(values)
    aces = values.count(11)
    while score > 21 and aces > 0:
        score -= 10
        aces -= 1
    return score

def has_usable_ace(hand):
    values = [get_card_value(c) for c in hand if c != "HIDDEN"]
    score = sum(values)
    aces = values.count(11)
    while score > 21 and aces > 0:
        score -= 10
        aces -= 1
    return aces > 0

class MultiPlayerBlackjackEnv(gym.Env):
    """
    Custom Environment that follows gym interface.
    Multi-player Blackjack: 0 (Human), 1 (Agent 1), 2 (Agent 2), and Dealer.
    """
    def __init__(self):
        super(MultiPlayerBlackjackEnv, self).__init__()
        self.action_space = spaces.Discrete(3)
        self.observation_space = spaces.Tuple((
            spaces.Discrete(32),
            spaces.Discrete(12),
            spaces.Discrete(2)
        ))
        
        self.deck = []
        self._refresh_deck()
        
        self.hands = [[], [], []]
        self.dealer_hand = []
        self.surrendered = [False, False, False]
        self.current_player = 0
        
    def _refresh_deck(self):
        suits = ['Bich', 'Co', 'Ro', 'Tep']
        values = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
        self.deck = [f"{v}{s}" for v in values for s in suits]
        random.shuffle(self.deck)
        
    def _draw_card(self):
        if not self.deck:
            self._refresh_deck()
        return self.deck.pop()

    def _get_obs(self, player_idx):
        hand = self.hands[player_idx]
        return (score_hand(hand), get_card_value(self.dealer_hand[0]), int(has_usable_ace(hand)))

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        if len(self.deck) <= 26:
            self._refresh_deck()
            
        self.current_player = 0
        self.surrendered = [False, False, False]
        
        self.hands = [[self._draw_card(), self._draw_card()] for _ in range(3)]
        self.dealer_hand = [self._draw_card(), self._draw_card()]
        
        return self._get_obs(self.current_player), {"current_player": self.current_player}
        
    def step(self, action):
        assert self.current_player < 3, "Round is already over."
        cp = self.current_player
        
        if action == 1:
            self.hands[cp].append(self._draw_card())
            if score_hand(self.hands[cp]) > 21:
                self.current_player += 1
        elif action == 0:
            self.current_player += 1
        elif action == 2:
            self.surrendered[cp] = True
            self.current_player += 1
            
        if self.current_player >= 3:
            while score_hand(self.dealer_hand) < 17:
                self.dealer_hand.append(self._draw_card())
            
            dealer_score = score_hand(self.dealer_hand)
            rewards = {}
            for i in range(3):
                if self.surrendered[i]:
                    rewards[i] = -0.5
                else:
                    score = score_hand(self.hands[i])
                    if score > 21:
                        rewards[i] = -1.0
                    elif dealer_score > 21:
                        rewards[i] = 1.0
                    elif score > dealer_score:
                        rewards[i] = 1.0
                    elif score == dealer_score:
                        rewards[i] = 0.0
                    else:
                        rewards[i] = -1.0
                        
            return self._get_obs(0), 0.0, True, False, {"rewards": rewards, "current_player": self.current_player}
        
        return self._get_obs(self.current_player), 0.0, False, False, {"current_player": self.current_player}
