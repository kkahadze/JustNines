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
        self.state["btl"] = int(hand.beatable(self) == True)
        self.state['tmc'] = unimplemented()

    def identify_action(self):
        """
        All actions are evaluated if they are available to the player, dependent on his hand and card_open.
        """
              
    def play_agent(self):
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
        self.identify_state()
        self.identify_action()
        
        # Agent selects action
        self.action = agent.step(self.state, self.actions)

        # Selected action searches corresponding card
        
        # Selected card is played
        self.card_play = card
        self.hand.remove(card)
        self.hand_play.pop()
        deck.discard(card)
        
        # Update Q Value           
        if algorithm == "q-learning":
            agent.update(self.state, self.action)
           

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
            

# 5. Turn
# -------------------------------------------------------------------------

class Turn(object):
    """
    Captures the process of a turn, that consists of:
        - Initialization of hand cards and open card before first turn
        - Chosen action by player
        - Counter action by oposite player in case of PL2 or PL4
    """
    
    def __init__(self, deck, player_1, player_2):
        """
        Turn is initialized with standard deck, players and an open card
        """
        
        self.deck = deck
        self.player_1 = player_1
        self.player_2 = player_2
        self.card_open = self.deck.draw_from_deck()
        self.start_up()
    
    def start_up(self):
        while self.card_open.value not in range(0,10):
            print (f'Inital open card {self.card_open.print_card()} has to be normal')
            self.card_open = self.deck.draw_from_deck()
        
        print (f'Inital open card is {self.card_open.print_card()}\n') 
        
        for i in range (7):
            self.player_1.draw(self.deck, self.card_open)
            self.player_2.draw(self.deck, self.card_open)
            
    def action(self, player, opponent):
        """
        Only reflecting the active players' action if he hand has not won yet.
        Only one player is leveraging the RL-algorithm, while the other makes random choices.
        """
        
        player_act = player
        player_pas = opponent
        player_act.evaluate_hand(self.card_open)

        self.count = 0
        
        # (1) When player can play a card directly
        if len(player_act.hand_play) > 0:
            
            if player_act == self.player_1:
                player_act.play_agent(self.deck, self.card_open)
            else:
                player_act.play_rand(self.deck)
                
            self.card_open = player_act.card_play
            player_act.evaluate_hand(self.card_open)

        # (2) When player has to draw a card
        else:
            print (f'{player_act.name} has no playable card')
            player_act.draw(self.deck, self.card_open)
            
            # (2a) When player draw a card that is finally playable
            if len(player_act.hand_play) > 0:
                
                if player_act == self.player_1:
                    player_act.play_agent(self.deck, self.card_open)
                else:
                    player_act.play_rand(self.deck)
                
                self.card_open = player_act.card_play
                player_act.evaluate_hand(self.card_open)
            
            # (2b) When player has not drawn a playable card, do nothing
            else:
                player_act.card_play = Card(0,0)
        
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
        while self.winner == 0: 
            self.turn.action()
            self.prev_cards = []
            
        self.player_1.identify_state()
        agent.update(self.player_1.state, self.player_1.action)
                
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