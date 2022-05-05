import gym
from gym import spaces
import numpy as np
import pandas as pd
from props import Card, Deck
from more_itertools import quantify
import datetime

class NineEnv(gym.Env):
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


    def reset(self, seed=None):
        # We need the following line to seed self.np_random
        # super().reset()

        self.played = None
        self.first_to_play = np.random.randint(0, 4)

        self._ord = (4 - self.first_to_play) % 4
        self._tot = 9

        self._set_players_cards() # this has to set self._jok
        self._set_calls() # this has to set self._tmc

        self.first_suit = None

        if self.first_to_play != 0: 
            self._pre_plays()
        else:
            self._btl = 1
        observation = self._get_obs()

        return observation

    def step(self, action): 
        # Map the action (element of {0,1,2,3}) to the card we play
        self._act(action)
        self._set_players_cards() 
        self._set_calls()
        self._tot -= 1
        self._post_plays()

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

    def _act(self, action):
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
        elif self._ord == 3: 
            self.first_suit = None
            self.hand_winner = self._winner()
        self.played[0] = card
        self._table[0].remove(card)
        return card

    def _get_highest(cards ,suit=None):
        '''Returns a joker if there is one in cards.
            Otherwise returns the highest valued card of the specified suit'''
        if not suit:
            return cards[np.argmax([card.value for card in cards])]
        else:
            acc = Card(0,0);[acc := Card(x,y) for x, y in map(lambda card: (card.value, card.suit), cards) if (suit == y and x > acc.value) or x == 13]
            return acc if acc else None

    def _get_obs(self):
        return (self._ord, self._tot, self._jok, self._btl, self._tmc)

    def _set_players_cards(self):
        self._table = [list(), list(), list(), list()]
        self._deck = Deck()
        self._deck.shuffle()
        for hand in self._table:
            self._deck.deal(hand, times=9)
        self._jok = quantify(map(lambda x: x.value == 13, self._table[0]))

    def _set_calls(self):
        self.calls = np.zeros((4))
        for i in range(4):
            cur_player = (self.first_to_play + i) % 4
            want = quantify(map(lambda x: x.value > 10, self._table[cur_player]))
            if i < 3 or want == 9 - self.calls.sum():
                self.calls[cur_player] = want
            else:
                if want > 0:
                    self.calls[cur_player] = want
                else:
                    self.calls[cur_player] = 0
        self._tmc = -1 * self.calls[0]

    def _playable(self, player):
        all = self._table[player]
        print(all)
        firsts = list(filter(lambda x: x.suit == self.first_suit, all))
        if not firsts:
            return all
        else:
            firsts.extend(list(filter(lambda x: x.value == 13, all)))
            return firsts
    
    def _choose_strg_beat(self, playable): 
        highest = self._get_highest(playable, suit=self.first_suit) 
        return highest if highest else self._get_highest(playable) 

    def _choose_weak_beat(self, playable): 
        beats = self._get_beats(playable) 
        if not beats:
            return self._choose_weak_loss(playable)
        for card in beats:
            if card.value < lowest.value:
                lowest = card
        return lowest

    def _choose_strg_loss(self, playable): 
        loses = self._get_loses(playable)
        if not loses:
            return self._choose_strg_beat(playable)
        else:
            highest = self._get_highest(playable, suit=self.first_suit)
            return highest if highest else self._get_highest(playable)
    
    def _choose_weak_loss(self, playable):
        acc = Card(13, 0); [acc := Card(value, suit) for (value, suit) in playable if value > acc.value]
        return acc

    def _get_winning_card(self):
        if not self.played.any():
            return None
        elif quantify(map(lambda x: x and x.value == 13, self.played)): # No shadow jokers
            return Card(13,0)
        else:
            firsts = list(filter(lambda x: x.suit == self.first_suit, self.played))
            firsts[np.argmax(card.value for card in firsts)]

    def _get_beats(self, playable):
        cur_winner = self._get_winning_card()
        if self.first_suit == None and cur_winner:
            return playable
        else:
            if cur_winner.value == 13:
                return list(filter(lambda x: x.value == 13))
            else:
                return list(filter(lambda x: x.value > cur_winner.value, playable))
    
    def _get_loses(self, playable):
        if self.first_suit == None:
            return playable
        loses = []
        for card in self.cards:
            if card.suit == self.first_suit and card.value < max([y.value for y in list(filter(lambda x : x.suit == self.first_suit))]):
                loses.append(card)
        return loses

    def _card_to_weight(self, card):
        weight = 0
        if card.value == 13:
            return 200
        if self.first_suit == card.suit:
            weight += 100
        return weight + card.value  

    def _winner(self):
        jok = 5
        joks = 0
        for i in range(4):
            cur = self.first_to_play + i
            if self.played[cur].value == 13:
                jok = cur
                joks += 1
        if joks:
            return jok
        else:
            weights = []
            for i in range(4):
                weights.append(self._card_to_weight(self.played[i]))
            return np.argmax(weights)

    def _play_rand(self, player):
        poss = self._playable(player)
        choice = poss[np.random.randint(0, len(poss))]
        self._table[player].remove(choice)
        self.played[player] = choice
        return choice

    def _pre_plays(self):
        self.played = np.ndarray((4), dtype=Card)
        for i in range(self._ord):
            cur = (self.first_to_play + i) % 4
            self.played[cur] = self._play_rand(cur)
            if i == 0 and self.played[cur].value != 13:
                self.first_suit = self.played[cur].suit
        self._btl = 1 if self._get_beats(self._playable(0)) else 0

    def _post_plays(self):
        for i in range(1, 4 - self._ord):
            cur = i % 4
            self.played[cur] = self._play_rand(cur)

        self.hand_winner = self._winner()
        self.first_suit = None
        self.played = None
        self._set_players_cards()
        self._set_calls() 