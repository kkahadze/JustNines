import random
import datetime
import numpy as np

def _get_highest(cards ,suit=None):
    '''Returns a joker if there is one in cards.
        Otherwise returns the highest valued card of the specified suit'''
    if not suit:
        return cards[np.argmax([card.value for card in cards])]
    else:
        acc = Card(0,0);[acc := Card(x,y) for x, y in map(lambda card: (card.value, card.suit), cards) if (suit == y and x > acc.value) or x == 13]
        return acc if acc else None

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
        random.seed(datetime.now())
        random.shuffle(self)

    def get(self, index):
        return self[index]

    def deal(self, location, times=1):
        for _ in range(times):
            location.cards.append(self.burn())

    def burn(self):
        return self.pop(0)

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