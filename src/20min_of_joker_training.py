from card_choice_gym import CardChoiceEnv
import numpy as np
import random
import pandas as pd
import csv

q = np.load('../models/q-table.npy')


def LearnJoker(q_in=np.zeros((4, 9, 3, 4, 19, 4)), alpha_in=0.01, epsilon_in=0.5, gamma_in=0.95, episodes_in=100):
  acts = ['STRG-BEAT', 'STRG-LOSS', 'WEAK-BEAT', 'WEAK-LOSS']
  env = CardChoiceEnv()

  alpha, gamma, epsilon = alpha_in, gamma_in, epsilon_in
  q = q_in

  wins = []
  good_calls = np.zeros((7,))

  for i in range(episodes_in):
    done = False
    s = env.reset()
    s0, s1, s2, s3, s4 = s
    while True:
      if np.random.random() < epsilon:
        # choose random action
        act_num = random.randint(0, 3)
      else:
        # greedy
        act_num = np.argmax(q[s0, s1, s2, s3, s4])

      action = acts[act_num]

      s_, r, done, _ = env.step(action)

      s_0, s_1, s_2, s_3, s_4 = s_
      td_target = r + gamma * np.argmax(q[s_0, s_1, s_2, s_3, s_4])
      td_error = td_target - q[s0, s1, s2, s3, s4, act_num]
      s = s_

      q[s0, s1, s2, s3, s4, act_num] += alpha * td_error
      if done:
        if r > 0:
          wins.append(i)
          good_calls = np.vstack((good_calls, [env.call_state]))

        break
  return wins, good_calls, q


eps = 20000
wins, calls, q = LearnJoker(epsilon_in=1, episodes_in=eps, q_in=q)
print(str(len(wins)/eps))

with open('../data/calls.csv', 'a+') as out:
    csv_out = csv.writer(out)
    # csv_out.writerow(['call','order', 'already', 'jokers', "aces", "kings", "queens"])
    for row in calls:
        csv_out.writerow(row)


def save_q_table(table):
    file = '../models/q-table.npy'
    with open(file, "wb"):
        np.save(file, table, allow_pickle=True)


save_q_table(q)
