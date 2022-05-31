from functools import cache
import numpy as np
import random
from more_itertools import quantify


def deal(self):
    self._table = [None, None, None, None]
    all = np.asarray([Card(value, suit) for value in range(4, 14) for suit in range(4) 
        if suit % 2 != 0 or (value != 4 and value != 13)], dtype=Card)
    np.random.shuffle(all)
    all = np.reshape(all, newshape=(4, 9))
    for i in range(4):
        self._table[i] = set(all[i])
    
def get_obs(self):
    # print((self._ord, self._tot , self._jok, self._btl, int(self._tmc + 9)))
    return (self._ord, self._tot , self._jok, self._btl, int(self._tmc + 9))

def set_players_cards(self): # SLOW
    self.deal()
    self._jok = quantify(map(lambda x: x.value == 13, self._table[0]))

def set_random_calls(self): # set random calls
    self.calls = np.zeros((4))
    for i in range(4):
        self.calls[i] = random.randint(0,9)

def set_calls(self):
    self.calls = np.zeros((4))
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

        if not cur_player: # and self.calling_model != None :
            # print("CORRECT CALLING")
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


# def playable(self, player):
#     all = self._table[player]
#     firsts = filter(lambda x: x.suit == self.first_suit, all)
#     if not firsts:
#         return all
#     else:
#         firsts = list(firsts)
#         firsts.extend(filter(lambda x: x.value == 13, all))
#         return firsts

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
            filtered = filter(lambda x: x.value == 13, playable)
            return
        else:
            return filter(lambda x: x and x.value > cur_winner.value, playable)

def get_loses(self, playable):
    if self.first_suit == None:
        return playable
    loses = []
    for card in playable:
        if card.suit == self.first_suit and card.value < max([y.value for y in filter(lambda x : x and x.suit == self.first_suit, playable)]):
            loses.append(card)
    return loses

@cache
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
    choice = random.choice(list(poss))
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
    self.first_suit = None
    self.played = None
    self._set_players_cards()

# def get_highest(cards ,suit=None):
#     '''Returns a joker if there is one in cards.
#         Otherwise returns the highest valued card of the specified suit'''
#     if not suit:
#         return cards[np.argmax([card.value for card in cards])]
#     else:
#         acc = None;[acc := Card(x,y) for (x, y) in map(lambda card: (card.value, card.suit), cards) if (not acc) or (suit == y and x > acc.value) or x == 13]
#         return acc if acc else None

def playable(self, player):
    all = self._table[player]
    if any(card.suit == self.first_suit for card in all):
        return filter(lambda card: card.suit == self.first_suit, all)
    else:
        return all

def in_playable(self, player, action):
    playable = self._playable(player)
    for card in playable:
        if card.value == action // 4 + 4 and card.suit == action % 4:
            return True
    return False

@cache
def model_predict(model, args_in):
    return model(np.asarray([list(args_in)]), training=False)

class Card(object):
    def __init__(self, value, suit):
        self.value = value
        self.suit = suit

    def __repr__(self):
        values = {
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

    def __hash__(self) -> int:
        return self.suit * 9 + self.value

    def __eq__(self, obj):
        return isinstance(obj, Card) and obj.value == self.value and obj.suit == self.suit



class Deck(list):
    def __init__(self):
        super().__init__([(Card(i, j)) for j in range(0,4) for i in range(5, 13)])
        # Ranks 7 through A are added
        # Ranks Six and Ace are added
        self.extend([Card(13, 0), Card(13, 0), Card(4, 0), Card(4, 2)]) 

    def __repr__(self):
        out = ""
        for card in self:
            out += (str(card) + "\n")
        return out

    def shuffle(self):
        # random.seed(datetime.datetime.now().timestamp())
        random.shuffle(self)

    def get(self, index):
        return self[index]

    def deal(self, location, times=1):
        for _ in range(times):
            location.append(self.pop(0))

class Player(object):
    def __init__(self, id_in):
        self.id = id_in
        self.score = 0
        self.cards = []
        self.called = 0
        self.taken = 0

    def __repr__(self):
        id = self.id
        return id

