import numpy as np
from astropy.io import fits
from astropy.time import Time


AU_METERS = 149597871000.0
AU_KM = 149597871.0


def calculate_deq(volume_dimles, radius):
    volume = volume_dimles * radius**3
    return (6*volume/np.pi)**(1.0/3.0)


def normalize(vec):
    return vec/np.linalg.norm(vec)


def solar_phase_angle_deg(target_pos, earth_pos):
    # to terget ref. frame
    sun_pos = target_pos * -1
    earth_pos = earth_pos - target_pos

    sun_pos = normalize(sun_pos)
    earth_pos = normalize(earth_pos)

    return np.arccos( np.dot(sun_pos, earth_pos)) * 180.0 / np.pi


def aspect_angle_deg(target_pos, earth_pos, lam, beta):
    # to terget ref. frame
    earth_pos = earth_pos - target_pos

    lam /= 180. * np.pi  # to radians
    beta /= 180. * np.pi

    pole_vec = np.array([np.cos(beta) * np.cos(lam), np.cos(beta) * np.sin(lam),
        np.sin(beta)])

    earth_pos = normalize(earth_pos)
    pole_vec = normalize(pole_vec)

    return np.arccos( np.dot(pole_vec, earth_pos)) * 180. / np.pi


def get_image_deg_per_pixel(filename):
    hdul = fits.open(filename)
    hdr = hdul[0].header
    if 'CD1_1' in hdr:
        cd11 = hdr['CD1_1']
        cd21 = hdr['CD2_1']
        hdul.close()

        deg_per_pixel = cd11/(np.cos(np.arctan2(cd21, cd11)))
    else:
        print(f"!!! No information on the resolution of the image: "
              f"{filename}. Inserting 0")
        deg_per_pixel = 0

    return deg_per_pixel

def jd_to_date(jd, fmt='ymdhms'):
    t = Time(jd, format='jd')
    t.format = fmt
    return t.value
