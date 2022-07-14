# from functools import cache
import numpy as np
import random
import datetime
from more_itertools import quantify
# from regex import cache_all

def table_to_binary(self):
    bin = np.zeros(36, dtype=int)
    for hand in self._table:
        for card in hand:
            if card.value == 13 and bin[34]:
                bin[35] = 1
            else:
                bin[self.card_to_index(card)] = 1
    return bin

def action_to_index(action):
    if action >= 35:
        return 35
    else:
        return action

def card_to_index(card): # never returns 35
    if card.value == 4:
        return card.suit / 2
    elif card.value == 13:
        return 34
    else:
        return (card.value - 5) * 4 + card.suit + 2

def update_gone(self, card):
    ind = card_to_index(card)
    if ind == 34 and self.gone[34]:
        self.gone[35] = True
    else:
        self.gone[ind] = True

def get_obs(self):
    return (
        self.gone[:9], self.gone[9:18], self.gone[18:27], self.gone[27:],
        self.taken[0], self.taken[1], self.taken[2], self.taken[3], 
        self.calls[0], self.calls[1], self.calls[2], self.calls[3], 
        self.first_suit if self.first_suit else 4,
        self.table_to_binary()
        )

def set_players_cards(self):
    self._table = [list(), list(), list(), list()]
    self._deck = Deck()
    self._deck.shuffle()
    for hand in self._table:
        self._deck.deal(hand, times=9)
    self._jok = quantify(map(lambda x: x.value == 13, self._table[0]))

def set_random_calls(self): # set random calls
    self.calls = np.zeros((4))
    for i in range(4):
        self.calls[i] = random.randint(0,9)

def set_calls(self):
    already = 0
    for i in range(4):
        cur_player = (self.first_to_play + i) % 4

        if not cur_player: # for call recording
            joks = quantify([card.value == 13 for card in self._table[0]])
            aces = quantify([card.value == 12 for card in self._table[0]])
            kings = quantify([card.value == 11 for card in self._table[0]])
            queens = quantify([card.value == 10 for card in self._table[0]])

        # quantify([x.value > 10 for x in self._table[cur_player]])    if random.randint(0,3) > 3 else
        # random.randint(0, 9) # DATA COLLECTION PURPOSES

        if self.calling_model != None and not cur_player:
            params = (self._ord, already, joks, aces, kings, queens)
            guess = np.argmax(model_predict(self.calling_model, params))
            # print(f"Guess {guess}")
            
        else:
            guess = quantify([x.value > 10 for x in self._table[cur_player]])

        want = guess if guess >= 0 else 0
        already += want
        # print(guess)
        if not cur_player:
            call_state = (want, self._ord, already, joks, aces, kings, queens)
        
        if i < 3 or want == 9 - self.calls.sum():
            self.calls[cur_player] = want
        else:
            self.calls[cur_player] = want
    self._tmc = -1 * self.calls[0]
    return call_state

def playable(self, player):
    all = self._table[player]
    firsts = list(filter(lambda x: x.suit == self.first_suit, all))
    if not firsts:
        return all
    else:
        firsts.extend(list(filter(lambda x: x.value == 13, all)))
        return firsts

def get_winning_card(self):
    if not self.played.any():
        return None
    elif quantify(map(lambda x: x and x.value == 13, self.played)): # No shadow jokers
        return Card(13,0)
    else:
        firsts = list(filter(lambda x: x and x.suit == self.first_suit, self.played))
        firsts[np.argmax([card.value for card in firsts])]

def get_beats(self, playable):
    cur_winner = self._get_winning_card() # returning None
    if self.first_suit == None or not cur_winner:
        return playable
    else:
        if cur_winner.value == 13:
            return list(filter(lambda x: x.value == 13, playable))
        else:
            return list(filter(lambda x: x and x.value > cur_winner.value, playable))

def get_loses(self, playable):
    if self.first_suit == None:
        return playable
    loses = []
    for card in playable:
        if card.suit == self.first_suit and card.value < max([y.value for y in list(filter(lambda x : x and x.suit == self.first_suit, playable))]):
            loses.append(card)
    return loses

def card_to_weight(self, card):
    weight = 0
    if card.value == 13:
        return 200
    if self.first_suit == card.suit:
        weight += 100
    return weight + card.value  

def winner(self, first):
    jok = 5
    joks = 0
    for i in range(4):
        cur = (first + i) % 4
        
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

def remove_from_table(self, player, suit, value):
    for card in self._table[player]:
        if (card.suit, card.value) == (suit, value):
            self._table[player].remove(card)
            break

def play_rand(self, player):
    poss = self._playable(player)
    choice = poss[random.randint(0, len(poss) - 1)]
    self.update_gone(choice)
    self._remove_from_table(player,choice.value, choice.suit)
    self.played[player] = choice
    return choice

def pre_plays(self):
    self.played = np.ndarray((4), dtype=Card)
    for i in range(self._ord):
        cur = (self.first_to_play + i) % 4
        temp = self._play_rand(cur)
        self.played[cur] = temp
        if i == 0 and self.played[cur].value != 13:
            self.first_suit = self.played[cur].suit
    self._btl = 1 if self._get_beats(self._playable(0)) else 0

def post_plays(self):
    for i in range(1, 4 - self._ord):
        cur = i % 4
        self.played[cur] = self._play_rand(cur)

    self.hand_winner = self._winner(self.first_to_play)
    self.taken[self.hand_winner] += 1
    self.first_suit = None
    self.played = None
    self._set_players_cards()

def get_highest(cards ,suit=None):
    '''Returns a joker if there is one in cards.
        Otherwise returns the highest valued card of the specified suit'''
    if not suit:
        return cards[np.argmax([card.value for card in cards])]
    else:
        acc = None
        for card in cards:
            if (acc and card.suit == suit and card.value > acc.value) or (card.suit == suit and not card):  
                acc = card
        return acc if acc else None
    
# @cache
def model_predict(model, args_in):
    arg1, arg2, arg3, arg3, arg5, arg6 = args_in
    return model.predict(np.expand_dims([arg1, arg2, arg3, arg3, arg5, arg6],axis=0))

def action_to_card(action):
    if action == 0:
        return Card(4, 0)
    elif action == 1:
        return Card(4, 2)
    elif action == 34:
        return Card(13, 0)
    elif action < 35:
        return Card((action - 2) // 4 + 5,(action - 2) % 4 )
    elif action < 39:
        return Card(3, action - 35)
    else:
        return Card(13, action - 39)

def play_card(self, playable, action): # new
    # if action < 34:

    return

class Card(object):
    def __init__(self, value, suit):
        self.value = value
        self.suit = suit

    def __repr__(self):
        values = {
            3: lambda: "Five",
            4: lambda: "Six",
            5: lambda: "Seven",
            6: lambda: "Eight",
            7: lambda: "Nine",
            8: lambda: "Ten",
            9: lambda: "Jack",
            10: lambda: "Queen",
            11: lambda: "King",
            12: lambda: "Ace",
            13: lambda: "Joker",
        }
        suits = {
            0: lambda : "Diamonds",
            1: lambda : "Clubs",
            2: lambda : "Hearts",
            3: lambda : "Spades",
        }
        
        value_name = values[self.value]()
        suit_name = suits[self.suit]()

        if value_name == "Joker":
            return "Joker"
        else:
            return value_name + " of " + suit_name

class Deck(list):
    def __init__(self):
        super().__init__()
        suits = list(range(4))
        values = list(range(5, 13))
        # Ranks 7 through A are added
        [[self.append(Card(i, j)) for j in suits] for i in values]
        # Ranks Six and Ace are added
        self.extend([Card(13, 0), Card(13, 0), Card(4, 0), Card(4, 2)]) 


    def __repr__(self):
        out = ""
        for card in self:
            out += (str(card) + "\n")
        return out

    def shuffle(self):
        random.seed(datetime.datetime.now().timestamp())
        random.shuffle(self)

    def get(self, index):
        return self[index]

    def deal(self, location, times=1):
        for _ in range(times):
            location.append(self.burn())

    def burn(self):
        return self.pop(0)

class Player(object):
    def __init__(self, id_in):
        self.id = id_in
        self.score = 0

    def __repr__(self):
        id = self.id
        return id