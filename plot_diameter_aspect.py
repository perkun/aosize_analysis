#!/bin/python
# created by perkun on 09/04/2021


import sqlite3
import argparse
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plot_latex


parser = argparse.ArgumentParser(
    description='''Plots aspect vs diameter''')
parser.add_argument("--db-name", required=True, help="name of database file",
                    type=str)
parser.add_argument("-o", "--output", required=False,
                    help="plot output filename", type=str)
args = parser.parse_args()

plot_latex.setLatex(width = 8, height = 6, dpi = 600)


con = sqlite3.connect(args.db_name)
cur = con.cursor()

data = pd.read_sql_query("SELECT id, deq_min, deq_max, deq_nominal, aspect FROM Images "
                         "WHERE deq_nominal != 0", con)

# print(data[['deq_min', 'deq_max']])
# print(data[['deq_min', 'deq_max']])

fig, axis = plt.subplots()
axis.errorbar(data['aspect'], data['deq_nominal'], [data['deq_nominal'] -
    data['deq_min'], data['deq_max'] - data['deq_nominal']], fmt='s')

axis.hlines(data['deq_nominal'].mean(), 0.0, 180., color='red', label='mean')

axis.set_xlabel('aspect')
axis.set_ylabel('diameter [km]')

axis.legend()
plt.tight_layout()

if args.output:
    fig.savefig(args.output, dpi=plot_latex.DPI)
else:
    plt.show()


con.commit()
con.close()
