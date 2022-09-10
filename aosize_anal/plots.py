
import matplotlib.font_manager as font_manager
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from aosize_anal.utils import jd_to_date


# DPI = 600

def set_latex(width=8, height=5.3):

#     global DPI
#     DPI = dpi

    pt = 20.36 * width / 8.0

    font_files = font_manager.findSystemFonts(
        fontpaths='/usr/share/texmf-dist/fonts/opentype/public/lm-math/')
    font_list = font_manager.createFontList(font_files)
    font_manager.fontManager.ttflist.extend(font_list)

    matplotlib.rcParams['font.family'] = 'Latin Modern Math'
    matplotlib.rcParams['font.size'] = pt
#     matplotlib.rcParams['text.usetex'] = True
    matplotlib.rcParams['mathtext.fontset'] = 'cm'

    matplotlib.rcParams["figure.figsize"] = [width, height]


def add_mean_min_max(database, axis, start, stop):
    res = database.execute(
        "SELECT deq_nominal, deq_min, deq_max, deq_plus, deq_minus "
        "FROM Results")[0]
    axis.hlines(res[0], start, stop,
                color='red', label=f'{round(res[0], 1)} km')

    axis.hlines(res[1],  start, stop,
                color='turquoise', label=f'+{round(res[3], 1)} km')
    axis.hlines(res[2], start, stop,
                color='turquoise', label=f'-{round(res[4],1)} km')
#         axis.annotate(f"mean={round(res[0], 1)} "
#                       f"+{round(res[3], 1)} -{round(res[4],1)} km",
#                       xycoords='axes fraction', xy=(0.05, 0.95))
    axis.legend()



def plot_aspect_diameter(database, width=8, height=6, dpi=600, filename="",
        latex=False, plot_mean=False, grid=False):

    if latex:
        set_latex(width=width, height=height)

    data = pd.read_sql_query(
            "SELECT id, deq_min, deq_max, deq_nominal, aspect FROM Images "
            "WHERE deq_nominal != 0", database.con)

    fig, axis = plt.subplots()

    if plot_mean:
        add_mean_min_max(database, axis, 0, 180)

    axis.errorbar(data['aspect'], data['deq_nominal'],
                  [
        data['deq_nominal'] - data['deq_min'],
        data['deq_max'] - data['deq_nominal']
    ],
        fmt='s')

    target = database.execute("SELECT target FROM Model")[0][0]
    plt.title(f"{target}")

    axis.set_xlabel('aspect')
    axis.set_ylabel('$D_{eq}$ [km]')

    if grid:
        plt.grid()
    plt.tight_layout()

    if filename:
        fig.savefig(filename, dpi=dpi)
    else:
        plt.show()


def plot_diameters(database, width=8, height=5.3, dpi=600, filename="",
                   latex=False, plot_mean=False, grid=False):

    if latex:
        set_latex(width=width, height=height)

    data = pd.read_sql_query(
        "SELECT id, jd, deq_min, deq_max, deq_nominal, aspect FROM Images "
        "WHERE deq_nominal != 0", database.con)

    matplotlib.rcParams["figure.figsize"] = [width, height]
    matplotlib.rcParams['font.size'] = 8
    fig, axis = plt.subplots()

    if plot_mean:
        add_mean_min_max(database, axis, data['id'].min(), data['id'].max())


    axis.errorbar(data['id'], data['deq_nominal'],
                  [
        data['deq_nominal'] - data['deq_min'],
        data['deq_max'] - data['deq_nominal']
    ],
        fmt='s')


#     axis.set_xlabel('image')
    times = [jd_to_date(i, fmt='iso') for i in data['jd']]
#     times = []
#     for i in data['jd']:
#         t = jd_to_date(i)
#         times.append(f"{t[3]}:{t[4]}:{round(t[5],0)}")

    target = database.execute("SELECT target FROM Model")[0][0]
    plt.title(f"{target}")

    plt.xticks(np.arange(data['id'].count()))
    axis.set_xticklabels(times, rotation=270)
    axis.set_ylabel('$D_{eq}$ [km]')
#     axis.set_ylabel('diameter [km]')


    if grid:
        plt.grid()
    plt.tight_layout()

    if filename:
        fig.savefig(filename, dpi=dpi)
    else:
        plt.show()
