import os.path
import numpy as np
from astropy.io import fits

from aosize_anal.utils import  solar_phase_angle_deg, aspect_angle_deg,  AU_KM
from aosize_anal.database import Database


def insert_images(database, list_filename, imgs_path):
    res = database.execute("SELECT lambda, beta FROM Model")
    lam = res[0][0]
    beta = res[0][1]

    # open file with the list of observations
    with open(list_filename, "r") as f_obs:
        for line in f_obs:
            elems = line.strip().split(" ")

            nr = int(elems[0])  # image id
            filename = os.path.abspath(os.path.join(imgs_path, elems[1]))

            if not os.path.isfile(filename):
                print(f"File {filename} does not exist!")
                continue

            jd = float(elems[2])

            ax = float(elems[4])  # asteroid position
            ay = float(elems[5])
            az = float(elems[6])

            ex = float(elems[7])  # earth position
            ey = float(elems[8])
            ez = float(elems[9])

            asteroid_pos = np.array([ax, ay, az])
            earth_pos = np.array([ex, ey, ez])
            spa = solar_phase_angle_deg(asteroid_pos, earth_pos)

            aspect = aspect_angle_deg(asteroid_pos, earth_pos, lam, beta)

            # resoultion kmppx
            hdul = fits.open(filename)
            hdr = hdul[0].header
            if 'CD1_1' in hdr:
                cd11 = hdr['CD1_1']
                cd21 = hdr['CD2_1']
                hdul.close()

                deg_per_pixel = cd11/(np.cos(np.arctan2(cd21, cd11)))
                distance = np.linalg.norm(asteroid_pos - earth_pos) * AU_KM
                kmppx = distance * np.tan(deg_per_pixel*np.pi/180.0)
            else:
                print(f"!!! No information on the resolution of the image {nr}: "
                      f"{filename}. Inserting kmppx = 0")
                kmppx = 0

            database.execute(f"INSERT INTO Images("
                        f"id, filename, jd, "
                        f"asteroid_x, asteroid_y, asteroid_z, "
                        f"earth_x, earth_y, earth_z, "
                        f"phase, aspect, kmppx) "
                        f"VALUES("
                        f"{nr}, '{filename}', {jd}, "
                        f"{ax}, {ay}, {az}, "
                        f"{ex}, {ey}, {ez}, "
                        f"{spa}, {aspect}, {kmppx})")

