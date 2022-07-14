from turtle import update
import gym
from gym import spaces
import numpy as np
from joker import *
import random
from keras.models import Sequential, load_model
from collections import defaultdict

class CardChoiceEnv(gym.Env):
    metadata = {"render_modes": ["human"], "render_fps": 2}

    def __init__(self):
        self.observation_space = spaces.Tuple((
            spaces.MultiBinary(9), # gone
            spaces.MultiBinary(9),
            spaces.MultiBinary(9),
            spaces.MultiBinary(9),
            spaces.Discrete(9), # taken
            spaces.Discrete(9),
            spaces.Discrete(9),
            spaces.Discrete(9),
            spaces.Discrete(9), # called
            spaces.Discrete(9),
            spaces.Discrete(9),
            spaces.Discrete(9),
            spaces.Discrete(5), # first suit
            spaces.MultiBinary(36), # table
        ))
        self.action_space = spaces.Discrete(43) # 0 - 34 normal (35), 35-38 waigos (4), 39-42 vishi (4)

        self.calling_model = None

    def reset(self):
        # We need the following line to seed self.np_random
        # super().reset()
            
        self.played = np.ndarray((4), dtype=Card)
        self.first_to_play = random.randint(0, 3)
        self.gone = np.zeros(36, dtype=np.bool)
        self.calls = np.zeros(4, dtype=int)
        self.taken = np.zeros(4, dtype=int)
        

        # self._ord = (4 - self.first_to_play) % 4
        # self._tot = 9

        self._set_players_cards() # this has to set self._jok

        # this has to set self._tmc, also for call recoridng
        self.call_state= self._set_calls()
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
        self._update_gone()
        self._post_plays()
        self._set_players_cards() 
        # self._tot -= 1

        # if self.hand_winner == 0:
        #     self._tmc += 1
        
        self.first_to_play = self.hand_winner
        # self._ord = (4 - self.first_to_play) % 4

        self.played = None
        self._pre_plays()

        left = 0
        for i in range(4):
            left += sum(self.observation_space[i])

        done = not bool(left)
        reward = 1 if self.observation_space[4] == self.observation_space[8] and done else 0   # No negative rewards
        observation = self._get_obs() # need update
        
        # No info
        return observation, reward, done, None

    def act(self, action):
        playable = self._playable(0) # needs to be tested

        card = self._play_card(playable, action)

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
        
        self._update_gone(card)

        # if card and card.value == 13: # This seems unneccessary, testing needs to be done, commenting out for now
        #     for card in self._table[0]:
        #         if card.value == 13:
        #             self._table[0].remove(card)
        #             break
        # else:
        #     self._remove_from_table(0, card.suit, card.value)
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
    _play_card = play_card
    _update_gone = update_gone
