# Libraries
# -------------------------------------------------------------------------
from props import Player, Card, Deck

# Custom libraries
import agents as ag
import state_action_reward as sar

# Public libraries
import numpy as np
import random
import time
from tqdm.notebook import tqdm
import sys, os


# 1. Print Functions
# -------------------------------------------------------------------------

def block_print():
    sys.__stdout__ = sys.stdout
    sys.stdout = open(os.devnull, "w")
    
def enable_print(): 
    sys.stdout = sys.__stdout__

def bold(string):
    chr_start = "\033[1m"
    chr_end = "\033[0m"
    print (chr_start + string + chr_end)
    
def underline(string):
    chr_start = "\033[4m"
    chr_end = "\033[0m"
    print(chr_start + string + chr_end)


# 4. Player
# -------------------------------------------------------------------------

class Player(object):
    """
    Player consists of a list of cards representing a players hand cards.
    Player can have a name, hand, playable hand. Thereform the players' state can be determined.
    """
    
    def __init__(self, id_in):
        # Added from original game
        self.id = id_in
        self.score = 0
        self.cards = []
        self.called = 0
        self.taken = 0

        # Part of original
        # self.name      = name
        # self.hand      = list()
        # self.hand_play = list()
        # self.card_play = 0
        
        self.state        = dict()
        self.actions      = dict()
        self.action       = 0
        agent.prev_state  = 0   
        
    def identify_state(self, hand):
        """
        The state of the player is identified by looping through players' hand for each property of the state.
        """
        self.state = dict()
        self.state["ord"] = hand.get_place_in_playing_order(self.id)
        self.state["tot"] = len(self.cards)
        self.state["jok"] = len(list(filter(lambda x: x.value == 13, self.cards)))
        self.state["btl"] = int(hand.beatable(self.id))
        self.state['tmc'] = self.taken = self.called

    def identify_action(self, hand):
        """
        All actions are evaluated if they are available to the player, dependent on his hand and card_open.
        """
        self.actions = dict()
        acts = ["STRG-BEAT", "WEAK-BEAT", "STRG-LOSS", "WEAK-LOSS"]
        for i, act in enumerate(acts):
            if i < 2:
                if self.state['btl'] != 0:
                    self.actions[act] = 1
                else:
                    self.actions[act] = 0
            else:  
                if hand.loseable():
                    self.actions[act] == 1
                else:
                    self.actions[act] = 0

# Cards removed from hand in following functions
    def play_agent(self, hand, prev):
        """
        Reflecting a players' intelligent move supported by the RL-algorithm, that consists of:
            - Identification of the players' state and available actions
            - Choose card_played
            - Remove card from hand & replace card_open with it
            - Update Q-values in case of TD
            
        Required parameters:
            - deck as deck
            - card_open as card
        """
        
        # Identify state & actions for action selection
        self.identify_state(hand)
        self.identify_action(hand)
        
        # Agent selects action
        self.action = agent.step(self.state, self.actions)

        # Selected action searches corresponding card
        being_played = self.choose_card(hand, prev)
        
        # Selected card is played
        self.cards.remove(being_played)

        
        # Update Q Value           
        if algorithm == "q-learning":
            agent.update(self.state, self.action, (len(self.cards) == 0 and self.taken == self.called))
        return being_played

    def play_rand(self):
        """
        Reflecting a players' random move, that consists of:
            - Shuffling players' hand cards
            - Lopping through hand cards and choosing the first available hand card to be played
            - Remove card from hand & replace card_open with it
        
        Required parameters: deck as deck
        """
        
        
        for card in self.hand:
            if card == self.hand_play[-1]:
                self.card_play = card
                self.hand.remove(card)
                self.hand_play.pop()
                deck.discard(card)
                print (f'\n{self.name} plays {card.print_card()}')
                break

        if (self.card_play.color == "WILD") or (self.card_play.value == "PL4"):
            self.card_play.color = self.choose_color()
            
    def choose_card(self, hand, prev):
        playable = self.playable(hand.first_suit)
        if self.action == 'STRG-BEAT':
            return self.choose_strg_beat(playable, hand)
        elif self.action == 'WEAK-BEAT':
            return self.choose_weak_beat(playable, hand, prev)
        elif self.action == 'STRG-LOSS':
            return self.choose_strg_loss(playable, hand)
        elif self.action == 'WEAK-LOSS':
            return self.choose_weak_loss(playable, hand)
        else:
            return None

    def playable(self, first_suit):
        firsts = list(filter(lambda x: x.suit == first_suit and not x.value == 13, self.cards))
        if len(firsts) == 0:
            return self.cards
        else:
            firsts.extend(list(filter(lambda x: x.value == 13, self.cards)))
            return firsts
        
    def choose_strg_beat(self, playable, hand): # check if first player for each of these functions
        highest = Card(0, 5)
        for card in playable:
            if card.value == 13:
                return card
            elif card.value > highest.value and (card.suit == hand.first_suit or hand.first_suit == 5):
                highest = card
        return highest

    def choose_weak_beat(self, playable, hand):
        beats = self.get_beats(hand, playable)
        lowest = beats[0]
        for card in beats:
            if card.value < lowest.value:
                lowest = card
        return lowest

    def choose_strg_loss(self, playable, hand):
        loses = self.get_loses(hand, playable)
        highest = loses[0]
        for card in loses:
            if card.value < highest.value:
                highest = card
        return highest

    def choose_weak_loss(self, playable, hand):
        lowest = Card(0, 5)
        for card in playable:
            if card.value < lowest.value:
                lowest = card
        return lowest

    def get_beats(self, hand, playable):
        if hand.first_suit == 5:
            return self.cards
        beats = []
        for card in self.cards:
            if card.value == 13 or card.suit == hand.first_suit and card.value > max([x.value for x in list(filter(lambda x : x.suit == hand.firstsuit, hand.prev_cards))]):
                beats.append(card)
        return beats
    
    def get_loses(self, hand, playable):
        if hand.first_suit == 5:
            return playable
        loses = []
        for card in self.cards:
            if card.suit == hand.first_suit and card.value < max([y.value for y in list(filter(lambda x : x.suit == hand.first_suit))]):
                loses.append(card)
        return loses



    



# 5. Turn
# -------------------------------------------------------------------------

class Turn(object):
    """
    Captures the process of a turn, that consists of:
        - Initialization of hand cards and open card before first turn
        - Chosen action by player
        - Counter action by oposite player in case of PL2 or PL4
    """

    def __init__(self): # need to set last_taker somewhere
        """
        Turn is initialized with standard deck, players and an open card
        """
        self.table = []
        self.first_s = 5
        
            
    def action(self, hand, player):
        """
        Only reflecting the active players' action if he hand has not won yet.
        Only one player is leveraging the RL-algorithm, while the other makes random choices.
        """

        if player == 0:
            played = (hand.users[player].play_agent(hand, self.table))
        else:
            played = (hand.users[player].play_rand(hand))
        self.table.append(played)
            
        if len(self.table) == 0:
            self.first_s = played.suit

        return played

    def winner(self):
        jok = 5
        joks = 0
        for i in range(0,4):
            if self.table[i].value == 13:
                jok = i
                joks += 1
        if joks == 2:
            return jok
        else:
            weights = []
            for i in range(4):
                weights.append(self.card_to_weight(self.table[i]))
            return (np.argmax(np.asarray(weights)))
    
    def card_to_weight(self, card):
        weight = 0
        if card.value == 13:
            return 200
        if self.first_s == card.suit:
            weight += 100
        return weight + card.value     

# 6. Hand
# -------------------------------------------------------------------------

class Hand(object): # Where are we resetting self.first_suit
    """
    A hand reflects an iteration of turns.
    It initialized with two players and a turn object.
    """
    
    def __init__(self):
        self.dealer = random.randint(0, 3)
        self.starting_player = (self.dealer + 1) % 4
        self.turn = Turn()
        self.prev_cards = []
        self.first_suit = 5
        self.users = [Player(0), Player(1), Player(2), Player(3)]

        # Playing all turns for one hand
        for i in range(9): # Representing 9 turns
            self.turn = Turn()
            self.prev_cards = []
            self.first_suit = 5
            for j in range(4): # Representing 4 "actions" per turn
                last_played = self.turn.action(self, (self.starting_player + j) % 4)
                self.prev_cards.append(last_played)
                if j == 0: self.first_suit = last_played.suit
            self.starting_player = (self.starting_player + self.turn.winner()) % 4
            
        self.users[0].identify_state()
        agent.update(self.users[0].state, self.users[0].action, (len(self.users[0].cards) == 0 and self.users[0].taken == self.users[0].called) )
                
    def get_place_in_playing_order(self, player_id):
        '''
            Returns an integer 0-3
        '''
        start = self.starting_player
        out = 5
        for i in range(0,4):
            if (start + i) % 4 == player_id:
                out = i
        return out

    def beatable(self, player):
        # How do we tell if a player can beat a hand with no wilds?
        # Either 
            # They have a Joker
            # They are the first to play
            # They have a higher first suit than all others

        if len(list(filter(lambda x: x.value == 13))) > 0 :
            return True
        if self.get_place_in_playing_order(player) == 0:
            return True

        cards = self.users[player].cards
        if [1 if len(list(filter(lambda x : x.suit == self.first_suit and (x.value > card.value and card.suit == self.first_suit ) , cards))) > 0 else 0 for card in self.prev_cards].count(0) > 0:
            return False
        else:
            return True

    def loseable(self, player):
        # if len(list(filter(lambda x: x.value == 13))) > 0 : # Must change when Joker rules are updated
            # return True
        if self.get_place_in_playing_order(player) == 0:
            return True
        if len(list(filter(lambda x: x.suit == self.first_suit, self.users[player].cards))) == 0:
            return True
        if [1 if len(list(filter(lambda x : x.suit == self.first_suit and (x.value < card.value and card.suit == self.first_suit ) , self.users[player].cards))) > 0 else 0 for card in self.prev_cards].count(0) > 0:
            return False
        else:
            return True

# 7. Tournament
# -------------------------------------------------------------------------

def tournament(iterations, algo):
    """
    A function that iterates various Games and outputs summary statistics over all executed simulations.
    """

    timer_start = time.time()
    
    # Selection of algorithm
    global agent, algorithm
    algorithm = algo
    
    if algo == "q-learning":
        agent = ag.QLearningAgent()
    else:
        agent = ag.MonteCarloAgent()
    
    
    winners, coverage = list(), list()
    agent.agent_init()

    for i in tqdm(range(iterations)):
        # time.sleep(0.01)

        if i%2 == 1:
            hand = Hand(starting_player)

        winners.append(hand.winner)
        coverage.append((agent.q != 0).values.sum())

    # Timer
    timer_end = time.time()
    timer_dur = timer_end - timer_start
    print (f'Execution lasted {round(timer_dur/60,2)} minutes ({round(iterations/timer_dur,2)} games per second)')
    
    return winners, coverage


# 8. Winning Condition
# -------------------------------------------------------------------------

# def check_win(player):
#     if len(player.hand) == 0:
#         return True