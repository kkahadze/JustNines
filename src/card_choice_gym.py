import gym
from gym import spaces
import numpy as np
from joker import *
import random

class CardChoiceEnv(gym.Env):
    metadata = {"render_modes": ["human"], "render_fps": 2}

    def __init__(self):
        self.observation_space = spaces.Tuple((
            spaces.Discrete(4),
            spaces.Discrete(9),
            spaces.Discrete(3),
            spaces.Discrete(4),
            spaces.Discrete(18),
        ))
        self.action_space = spaces.Discrete(4)

    def reset(self):
        # We need the following line to seed self.np_random
        # super().reset()

        self.played = np.ndarray((4), dtype=Card)
        self.first_to_play = random.randint(0, 3)

        self._ord = (4 - self.first_to_play) % 4
        self._tot = 9

        self._set_players_cards() # this has to set self._jok

        self.call_state = self._set_calls() # this has to set self._tmc, also for call recoridng
        self.player_call = -1 * self._tmc # for call recording

        self.first_suit = None

        if self.first_to_play != 0: 
            self._pre_plays()
        else:
            self._btl = 1
        observation = self._get_obs()

        return observation

    def step(self, action): 
        # Map the action (element of {0,1,2,3}) to the card we play
        self.act(action)
        self._post_plays()
        self._set_players_cards() 
        self._set_calls()
        self._tot -= 1

        if not self.hand_winner:
            self._tmc += 1
        
        self.first_to_play = self.hand_winner
        self._ord = (4 - self.first_to_play) % 4

        self.played = None
        self._pre_plays()
        done = self._tot == 0
        reward = 1 if self._tmc == 0 and done else 0   # No negative rewards
        observation = self._get_obs()
        
        # No info
        return observation, reward, done, None

    def act(self, action):
        playable = self._playable(0)
        if action == 'STRG-BEAT':
            card = self._choose_strg_beat(playable)
        elif action == 'WEAK-BEAT':
            card = self._choose_weak_beat(playable)
        elif action == 'STRG-LOSS':
            card = self._choose_strg_loss(playable)
        elif action == 'WEAK-LOSS':
            card = self._choose_weak_loss(playable)
        else:
            return None

        if self._ord == 0:
            self.first_suit = card.value
            self.played = np.ndarray((4), dtype=Card)
            self.played[0] = card
        elif self._ord == 3: 
            self.first_suit = None
            self.played[0] = card
            self.hand_winner = self._winner(self.first_to_play)
        else:
            self.played[0] = card

        if card and card.value == 13:
            for card in self._table[0]:
                if card.value == 13:
                    self._table[0].remove(card)
                    break
        else:
            self._remove_from_table(0, card.suit, card.value)
        return card
    
    # Joker game related functions
    _get_obs = get_obs
    _set_players_cards = set_players_cards
    _set_calls = set_calls
    _playable  = playable
    _choose_strg_beat = choose_strg_beat
    _choose_strg_loss = choose_strg_loss
    _choose_weak_beat = choose_weak_beat
    _choose_weak_loss = choose_weak_loss
    _play_rand = play_rand
    _winner = winner
    _pre_plays, _post_plays = pre_plays, post_plays
    _remove_from_table = remove_from_table
    _get_beats = get_beats
    _get_winning_card = get_winning_card
    _card_to_weight = card_to_weight
    _get_loses = get_loses
    _set_random_calls = set_random_calls
