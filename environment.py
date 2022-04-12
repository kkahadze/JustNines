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
        self.hand      = list()
        self.hand_play = list()
        self.card_play = 0
        
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

    def play_agent(self, hand):
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
        being_played = self.choose_card(hand)
        # Selected card is played
        self.card_play = card
        self.hand.remove(card)
        self.hand_play.pop()
        deck.discard(card)
        
        # Update Q Value           
        if algorithm == "q-learning":
            agent.update(self.state, self.action, (len(self.cards) == 0 and self.taken == self.called))

    def play_rand(self, deck):
        """
        Reflecting a players' random move, that consists of:
            - Shuffling players' hand cards
            - Lopping through hand cards and choosing the first available hand card to be played
            - Remove card from hand & replace card_open with it
        
        Required parameters: deck as deck
        """
        
        random.shuffle(self.hand_play)
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
            
    def choose_card(self, hand):
        playable = self.playable(hand.first_suit)
        if self.action == 'STRG-BEAT':
            self.choose_strg_beat(playable, hand)
        elif self.action == 'WEAK-BEAT':
            self.choose_weak_beat(playable, hand)
        elif self.action == 'STRG-LOSS':
            self.choose_strg_loss(playable, hand)
        elif self.action == 'WEAK-LOSS':
            self.choose_weak_loss(playable, hand)

    def playable(self, first_suit):
        firsts = list(filter(lambda x: x.suit == first_suit and not x.value == 13, self.cards))
        if len(firsts) == 0:
            return self.cards
        else:
            firsts.extend(list(filter(lambda x: x.value == 13, self.cards)))
            return firsts

# 5. Turn
# -------------------------------------------------------------------------

class Turn(object):
    """
    Captures the process of a turn, that consists of:
        - Initialization of hand cards and open card before first turn
        - Chosen action by player
        - Counter action by oposite player in case of PL2 or PL4
    """
    
    def __init__(self,): # need to set last_taker somewhere
        """
        Turn is initialized with standard deck, players and an open card
        """
        
        self.deck = deck
        self.card_open = self.deck.draw_from_deck()
        self.last_taker = None
        self.start_up()
    
    def start_up(self):
        for i in range (7):
            self.player_1.draw(self.deck, self.card_open)
            self.player_2.draw(self.deck, self.card_open)
            
    def action(self, hand, player):
        """
        Only reflecting the active players' action if he hand has not won yet.
        Only one player is leveraging the RL-algorithm, while the other makes random choices.
        """
        self.count = 0
        

        if player == 0:
            hand.users[player].play_agent(hand)
        else:
            hand.users[player].play_rand(self.deck)
            
        self.card_open = player_act.card_play
        player_act.evaluate_hand(self.card_open)


        
        if check_win(player_act) == True: return
        if check_win(player_pas) == True: return
        

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
        self.turn = Turn(deck = Deck())
        self.prev_cards = []
        self.first_suit = 5

        # Playing all turns for one hand
        for i in range(9): # Representing 9 turns
            for j in range(4): # Representing 4 "actions" per turn
                self.turn.action(self, (self.starting_player + j) % 4)
                self.prev_cards = []
                self.starting_player = self.turn.last_taker
            
        self.users[0].identify_state()
        agent.update(self.users[0].state, self.users[0].action)
                
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