import csv
import numpy as np

def save_q_table(table):
    file = '../models/q-table.npy'
    with open(file, "wb"):
        np.save(file, table, allow_pickle=True)

def write_calls(calls):
    with open('../data/calls.csv', 'a+') as out:
        csv_out = csv.writer(out)
        # csv_out.writerow(['call','order', 'already', 'jokers', "aces", "kings", "queens"])
        for row in calls:
            csv_out.writerow(row)
