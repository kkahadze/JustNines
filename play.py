from joker import *
import random

class Nine(object):
    def __init__(self):
        self.cards = [list(), list(), list(), list()]
        self.played = np.ndarray(shape=(4), dtype=Card)
        self.dealer = random.randint(0, 3)
        self.taken = np.zeros((4))
        self.calls = np.zeros((4))
        
        self.first_suit = None # placeholder

    def start(self):
        self.deal()
        self.show_cards()

        for i in range(1, 5):  # each player must call
            cur = (self.dealer + i) % 4
            if not cur:
                call = self.get_player_call(i - 1)  # order is 0-indexed
            else:
                call = self.get_bot_call(i - 1)
            self.calls[cur] = call
        self.show_calls()
        first = (self.dealer + 1) % 4
        for i in range(9):  # each player must play each card
            for j in range(4):
                if not first + j:
                    self.show_player_cards()
                    card = self.get_player_card()
                else:
                    card = self.get_bot_card((first + j) % 4, 9 - i)
                self.played[(first + j) % 4] = card

            winner = self._winner(first)
            self.show_hand_winner(winner)
            first = winner
            self.show_taken()
            self.played = np.ndarray(shape=(4), dtype=Card)
        self.show_final_points()

    def deal(self):
        deck = Deck()
        deck.shuffle()
        for i in range(4):
            deck.deal(self.cards[i], 9)

    def show_cards(self):
        print("Cards:")
        for card in self.cards[0]:
            print(card)

    def get_player_call(self, ord):
        already = self.calls.sum()
        if ord == 3 and already <= 9:
            cant = 9 - already
            print("You can not call", cant)
            called = None
            while (not called) or (called == already):
                print("How much would you like to call?")
                called = int(input())
        else:
            print("How much would you like to call?")
            called = int(input())
        return called

    def get_bot_call(self, ord):
        already = self.calls.flatten().sum()
        print("Already called", already)
        if ord == 3 and already <= 9:
            cant = 9 - already
            called = None
            print("Player " + str((self.dealer + ord) %
                  4) + " can not call", cant)
            while called != cant:
                called = random.randint(0, 9)
            print("Player " + str((self.dealer + ord) %
                  4) + " called " + str(called))
        else:
            called = random.randint(0, 9)
            print("Player " + str((self.dealer + ord) %
                  4) + " called " + str(called))
        return called

    def show_calls(self):
        for i in range(4):
            print("Player " + str(i) + " called  " + str(self.calls[i]))

    def get_player_card(self):
        choice = self.cards[0][int(input())]
        print("You chose ", choice)
        return choice

    def show_player_cards(self):
        print("Your cards are ", self.cards[0])

    def get_bot_card(self, user_number, num_cards):
        choices = self.playable(user_number)
        choice = choices[random.randint(0, num_cards - 1)]
        print("Bot " + str(user_number) + " chose " + str(choice))
        return choice

    def show_hand_winner(self, winner):
        self.taken[winner] += 1
        print("The winner of this hand is player ", winner)

    def show_taken(self):
        for i in range(4):
            print("Player " + str(i) + " has taken " + str(self.taken[i]))

    def show_final_points(self):
        pts = [(take - 1) * 50 + 100 if take == call else take *
               10 for take, call in zip(self.taken, self.calls)]
        print(pts)

    def playable(self, player):
        all = self.cards[player]
        firsts = list(filter(lambda x: x.suit == self.first_suit, all))
        if not firsts:
            return all
        else:
            firsts.extend(list(filter(lambda x: x.value == 13, all)))
            return firsts
    
    def load_q_table(self):
        with open('q-table', 'r') as f:
            q_in = f.read()
        self.q = q_in

    _winner = winner
    _card_to_weight = card_to_weight


game = Nine()
game.start()
