#!/bin/python

from subprocess import call, check_output
import argparse
import pandas as pd
import os.path

from aosize_anal.database import Database
from aosize_anal.utils import jd_to_date


parser = argparse.ArgumentParser(description='''Make projesctions''')
parser.add_argument("--db-name", required=True,
                    help="name of database file", type=str)

args = parser.parse_args()

db = Database(args.db_name)

imgdata = pd.read_sql_query("SELECT * FROM Images", db.con)
modeldata = pd.read_sql_query("SELECT * FROM Model", db.con)
# print(modeldata.loc[0])
modeldata = modeldata.loc[0]

## wziąć z fitsa?
img_size = 256

# kąty
alpha = modeldata['lambda'] + 90.0
beta = 90.0 - modeldata['beta']

for index, row in imgdata.iterrows():

    date = jd_to_date(row['jd'], fmt='iso')

    gamma = (row['jd'] - modeldata['jd_g0'])/(modeldata['period']/24.0)
    gamma *= 360
    gamma += 270.0 + modeldata['gamma']

    while gamma > 360.0:
        gamma -= 360.0

    while gamma < 0.0:
        gamma += 360.0


    # prepare synthetic projection to tmp.png
    commad = f'viewer {modeldata["filename"]} -a {alpha} {beta} {gamma} ' \
    f'-mp {row["asteroid_x"]} {row["asteroid_y"]} {row["asteroid_z"]} ' \
    f'-cp {row["earth_x"]} {row["earth_y"]}  {row["earth_z"]} ' \
    f'-xyz -f tmp'
    call(commad, shell = True)

    s = row['scale']
    ds = 20.0
    size = s + ds
    position = int(round((img_size/2 - size/2), 0))
    sf = float(s)/float(size) * 100
    sf = int(round(sf, 0))

    call(f'convert tmp.png -resize {sf}\% tmp.png', shell=True)
    call(f'convert tmp.png -gravity center -background black -extent 800x800 tmp.png', shell=True)

    #########

    # find photocenter of observation (call external program img_center)
    output = check_output(f"img_center {row['filename']}", shell=True,
            text=True).strip().split(" ")
    corner_x = int(output[0]) - size/2
    corner_y = img_size - int(output[1]) - size/2



    # prepare observation
    call(f'convert {os.path.splitext(row["filename"])[0] + ".png"} -crop {size}x{size}+{corner_x}+{corner_y} tmp2.png', shell=True)
    call("convert tmp2.png -resize 800x800 tmp2.png", shell=True)
    call('convert tmp2.png tmp.png +append +repage tmp3.png', shell=True)

    new_filename = os.path.splitext(row["filename"])[0] + "_COMP.png"
    call(f'convert tmp3.png -pointsize 60 -fill white -gravity center -annotate +0+350 \"{date}\" {new_filename}', shell=True)


    # make overlays:
#     commad = f'viewer {modeldata["filename"]} -a {alpha} {beta} {gamma} ' \
#     f'-mp {row["asteroid_x"]} {row["asteroid_y"]} {row["asteroid_z"]} ' \
#     f'-cp {row["earth_x"]} {row["earth_y"]}  {row["earth_z"]} ' \
#     f'-f tmp -v {1/(sf/100)}'
#     call(commad, shell = True)
#
#     print(sf)
#
#     exit()
#     # find photocenter of observation (call external program img_center)
# #     call(f'convert tmp.png -resize {sf}\% tmp.png', shell=True)
# #     print(800*sf/100)
# #     exit()
#
#     output = check_output(f"img_center tmp.png", shell=True,
#             text=True).strip().split(" ")
#
#     corner_x = int(output[0]) - (800*sf/100)/2
#     corner_y = (800*sf/100) - int(output[1]) - (800*sf/100)/2
#     call(f'convert tmp.png -gravity +{int(corner_x)}{int(corner_y)} -background black -extent 800x800 tmp.png', shell=True)
#
#     call(commad, shell = True)
#     call('convert tmp.png -fuzz 90% -fill red -opaque white tmp.png',
#             shell=True)
#
#     call('convert tmp2.png -colorspace sRGB -type truecolor tmp2.jpg', shell=True)
#     call('convert tmp2.jpg -fuzz 90% -fill blue -opaque white tmp2.png', shell=True)
#
#     new_filename = os.path.splitext(row["filename"])[0] + "_OVERLAY.png"
#     call(f'convert tmp.png tmp2.png -compose colorize -composite {new_filename}', shell=True)

#     call("rm tmp.png tmp2.png tmp2.jpg tmp3.png", shell=True)
    call("rm tmp.png tmp2.png tmp3.png", shell=True)
