import state_action_reward as sar

import pandas as pd
import numpy as np
import random

class QLearningAgent(object):
    
    def agent_init(self, agent_init_info):
        """
        Initializes the agent to get parameters and import/create q-tables.
        Required parameters: agent_init_info as dict
        """
        
        self.states      = sar.states()
        self.actions     = sar.actions()
        self.prev_state  = 0
        self.prev_action = 0
        
        #  Store the parameters provided in agent_init_info

        self.epsilon     = agent_init_info["epsilon"]
        self.step_size   = agent_init_info["step_size"]
        self.new_model   = agent_init_info["new_model"]
        self.R           = sar.rewards(self.states, self.actions) # Could this be more efficient as a Counter since it is sparse    

        
        # (2) Create Q-table that stores action-value estimates, initialized at zero
        if self.new_model == True:
            self.q = pd.DataFrame(data    = np.zeros((len(self.states), len(self.actions))), 
                                  columns = self.actions, 
                                  index   = self.states)
            
            self.visit = self.q.copy()
        
        
        # (3) Import already existing Q-values and visits table if possible
        else:
            try:
                self.q            = pd.read_csv("../assets/files/q-learning-q.csv", sep = ";", index_col = "Unnamed: 0")
                self.q.index      = self.q.index.map(lambda x: eval(x))
                self.q["IDX"]     = self.q.index
                self.q            = self.q.set_index("IDX", drop = True)
                self.q.index.name = None

                self.visit            = pd.read_csv("../assets/files/q-learning-visits.csv", sep = ";", index_col = "Unnamed: 0")
                self.visit.index      = self.visit.index.map(lambda x: eval(x))
                self.visit["IDX"]     = self.visit.index
                self.visit            = self.visit.set_index("IDX", drop = True)
                self.visit.index.name = None

            # (3a) Create empty q-tables if file is not found
            except:
                print ("Existing model could not be found. New model is being created.")
                self.q = pd.DataFrame(data    = np.zeros((len(self.states), len(self.actions))), 
                                      columns = self.actions, 
                                      index   = self.states)

                self.visit = self.q.copy()

    def step(self, state_dict, actions_dict):
        """
        Choose the optimal next action according to the followed policy.
        Required parameters:
            - state_dict as dict
            - actions_dict as dict
        """
        
        # (1) Transform state dictionary into tuple
        state = [i for i in state_dict.values()]
        state = tuple(state)
        
        # (2) Choose action using epsilon greedy
        # (2a) Random action
        if random.random() < self.epsilon:
            
            actions_possible = [key for key,val in actions_dict.items() if val != 0]         
            action = random.choice(actions_possible)
        
        # (2b) Greedy action
        else:
            actions_possible = [key for key,val in actions_dict.items() if val != 0]
            random.shuffle(actions_possible)
            val_max = 0
            
            for i in actions_possible:
                val = self.q.loc[[state],i][0]
                if val >= val_max: 
                    val_max = val
                    action = i
        
        return action
    
    def update(self, state_dict, action, won):
        """
        Updating Q-values according to Belman equation
        Required parameters:
            - state_dict as dict
            - action as str
        """
        state = [i for i in state_dict.values()]
        state = tuple(state)
        
        # (1) Set prev_state unless first turn
        if self.prev_state != 0:
            prev_q = self.q.loc[[self.prev_state], self.prev_action][0]
            this_q = self.q.loc[[state], action][0]
            if won:
                reward = 1
            else:
                reward = 0
            
            # Calculate new Q-values
            if reward == 0:
                self.q.loc[[self.prev_state], self.prev_action] = prev_q + self.step_size * (reward + this_q - prev_q) 
            else:
                self.q.loc[[self.prev_state], self.prev_action] = prev_q + self.step_size * (reward - prev_q)
                
            self.visit.loc[[self.prev_state], self.prev_action] += 1
            
        # (2) Save and return action/state
        self.prev_state  = state
        self.prev_action = action

    
    