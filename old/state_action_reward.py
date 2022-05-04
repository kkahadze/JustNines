import pandas as pd
import numpy as np
import itertools
from collections import Counter, defaultdict
# Implemented with no wildcard!

def states():
    round_params = {"ORD": 4} # Place in order
    cards_in_hand = {"TOT" : 9, "JOK":3} # In hand, wilds, joks
    dependent = {"BTL":2, "TMC" : 18} # beatable,  taken - called

    # Combine dictionaries
    states_dict  = {**round_params, **cards_in_hand, **dependent}
    states = []

    for val in states_dict.values():
        aux = range(0,val)
        states.append(aux)

    # Conduct all combinations
    states = list(itertools.product(*states))
    states_all = list()

    # Need to replace conditions.
    for i in range(len(states)):
        if (not(states[i][2] > states[i][1])) and states[i][4] < states[i][2]:
            states_all.append(states[i])
    states_all.append((0,0,2,0,0))
    return states_all

def actions():
    actions_all = ["STRG-BEAT", "WEAK-BEAT", "STRG-LOSS", "WEAK-LOSS"]    
    return actions_all

def rewards(states, actions):
    
    R = np.zeros((len(states), len(actions)))
    
    for i in range(len(states)): # rewards! (end state) setting
        R[len(states - 1)] = 1 # entire row of predicted value set to 1

    R = pd.DataFrame(data = R, 
                     columns = actions, 
                     index = states)

    return R
