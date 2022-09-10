#!/bin/python
# created by perkun on 14/04/2021

from aosize_anal.database import Database
from aosize_anal.model import Model
from aosize_anal.insert_images import insert_images
from aosize_anal.calculate_sizes import calculate_sizes
from aosize_anal.get_deq import get_deq_unweighted, get_deq_weighted, \
    AspectRange
from aosize_anal.plots import plot_aspect_diameter, plot_diameters
import os.path
import os
import sys
import argparse


def decompose_aspects(aspects_str):
    aspect_ranges = []
    for r in aspects_str:
        x, y = r.split(",")
        ar = AspectRange()
        ar.min_aspect = float(x)
        ar.max_aspect = float(y)
        aspect_ranges.append(ar)
    return aspect_ranges


def main():
    parser = argparse.ArgumentParser(description='''Diamaters analysis''')

#     parser.add_argument("-a", "--action",  help="action to perform",
#                         required=True,
#                         choices=['create', 'insert'])
    action_group = parser.add_argument_group("ACTIONS")
    action_group.add_argument("--create", action='store_true')
#     action_group.add_argument("--insert", action='store_true')
    action_group.add_argument("--calculate", action='store_true')
    action_group.add_argument("--get", choices=['deq'],
        help="get values calulated from database")

    action_group.add_argument("--plot", help="Make some plots",
            choices=['diameters', 'aspect-diameter'])

    parser.add_argument("--db-name", required=True,
                        help="name of database file", type=str)

    create_group = parser.add_argument_group("Create action options")
    create_group.add_argument("-o", "--override", action='store_true',
                              help="override existing database")

    create_group.add_argument("--obj", required=False,
                              help="model parameters from OBJ header", type=str)
    create_group.add_argument("--img-list",
                              help="filename with the list of AO observations",
                              type=str)
    create_group.add_argument("--img-dir",
                              help="directory name with obserwations", type=str)

    calculate_group = parser.add_argument_group("Calculate action options")
    calculate_group.add_argument("--diameters",
        help="name of the file containing diameters (aosize output)",
        type=str)
    calculate_group.add_argument("--scale",
        help="Recalculate radius from scale and fits' information (rather than"
        "from diameters file)",
        action='store_true')
    calculate_group.add_argument("--volume-factor",
        help="multiply dimless volume by this factor", type=float)

    get_group = parser.add_argument_group("Get action options")
#     get_group.add_argument("--deq",
#         help="calculate equivalent sphere diameters", action='store_true')
    get_group.add_argument("--aspects",
        help="Specify aspect ranges, e.g. --aspects 20,30 45,60",
                           nargs="+")

    plot_group = parser.add_argument_group("Plot action options")
#     plot_group.add_argument("--aspect-diameter", help="aspect vs diameter",
#             action='store_true')
#     plot_group.add_argument("--deqs", help="diameters",
#             action='store_true')
    plot_group.add_argument("--output", help="output filename")
    plot_group.add_argument("--latex", help="font and size for publication",
            action='store_true')
    plot_group.add_argument("--mean", help="plot mean and +/- values",
            action='store_true')
    plot_group.add_argument("--grid", help="plot grid",
            action='store_true')


    args = parser.parse_args()


    db_exists = os.path.isfile(args.db_name)
    if not db_exists and not args.create:
        print("Database does not exist!")
        exit()

    db = Database(args.db_name)
    db.speedup()

    if args.create:
        db.create()
#         if db_exists:
#             if args.override:
#                 print("Database already exists, overriding")
#                 db.create()
#             else:
#                 print("Database already exists, exiting")
#                 os.remove(args.db_name)
#                 exit()

        model = Model()
        if args.obj:
            model.read_from_obj(args.obj)
            model.update_table(db)
            print(model)
        else:
            print("Model file not specified")
            exit()

        if args.img_list and args.img_dir:
            insert_images(db, args.img_list, args.img_dir)
        else:
            print("Images list and dir not specified")

    if args.calculate:
        if not args.diameters:
            print("diameter file not specified")
            exit()
        if not os.path.isfile(args.diameters):
            print("File with diameters does not exist")
            exit()
        if args.volume_factor:
            calculate_sizes(db, args.diameters, args.scale, args.volume_factor)
        else:
            calculate_sizes(db, args.diameters, args.scale)

    if args.get:
        if args.get == 'deq':
            if not args.aspects:
                print("Specify aspect ranges")
                exit()

            deq, deq_plus, deq_minus = get_deq_unweighted(db)
            print("NOT WIGHTED")
            print(f"{round(deq,2)} +{round(deq_plus,2)} "
                  f"-{round(deq_minus, 2)}")

            print("-" * 80)
            print("WEIGHTED")

            deq_nominal, deq_plus, deq_minus, ranges = get_deq_weighted(
                db, decompose_aspects(args.aspects))
            print("range".ljust(16), "deq")
            for ar in ranges:
                tmp_deq_plus = round(ar.deq_max - ar.deq_nominal, 2)
                tmp_deq_minus = round(ar.deq_nominal - ar.deq_min, 2)
                print(f"[{ar.min_aspect}, {ar.max_aspect}]:".ljust(16),
                      f"{round(ar.deq_nominal, 2)} +{tmp_deq_plus} "
                      f"-{tmp_deq_minus} km",
                      f"({round(ar.avg_kmppx,2)} avg kmppx)")

            print(f"{round(deq_nominal, 2)} +{round(deq_plus,2)} "
                  f"-{round(deq_minus,2)}")

    if args.plot:
        if args.plot == 'aspect-diameter':
            plot_aspect_diameter(db, filename=args.output, latex=args.latex,
                                 plot_mean=args.mean, grid=args.grid)
        if args.plot == 'diameters':
            plot_diameters(db, filename=args.output, latex=args.latex,
                           plot_mean=args.mean, grid=args.grid)


if __name__ == "__main__":
    main()
