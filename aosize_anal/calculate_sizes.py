import os.path
import numpy as np
from aosize_anal.utils import AU_KM, get_image_deg_per_pixel, calculate_deq


def decompose_line(line):
    elements = line.strip().split(';')
    clone_id = int(elements[0])
    volume_dimles = float(elements[1])

    images_data = []
    for elem in elements[2:]:
        if elem == '':
            continue
        # TODO zmienić na nowy format

        sub_elements = elem.strip().split(':')
        data = {}
        data['img_nr'] = int(sub_elements[0])
        data['scale'] = int(sub_elements[1])
        data['rmsd'] = float(sub_elements[2])         # [pix]
        data['radius'] = float(sub_elements[3])/1000.0  # [km]

        # OLD
#         data['img_nr'] = int(sub_elements[0])
#         data['radius'] = float(sub_elements[1])/1000.0    # [km]
#         data['rmsd'] = float(sub_elements[2])             # [pix]
#         data['scale'] = 33                                # rubbish
        images_data.append(data)

    return clone_id, volume_dimles, images_data


def calculate_nominal_sizes(database, diameters_fn, scale_from_fits,
        volume_factor):
    f_diameters = open(diameters_fn, "r")
    line = f_diameters.readline()
    f_diameters.close()

    clone_id, volume_dimles, images_data = decompose_line(line)

    if clone_id != 1:
        print("First line does not contain nominal model (id = 1)!, exiting")
        exit()

    nominal_radiuses = {}
    nominal_scales = {}

    for data in images_data:
        img_nr = data['img_nr']
        radius = data['radius']
        scale = data['scale']

        if img_nr not in nominal_radiuses:
            nominal_radiuses[img_nr] = np.array([radius])
        else:
            nominal_radiuses[img_nr] = np.append(
                nominal_radiuses[img_nr], radius)

        if img_nr not in nominal_scales:
            nominal_scales[img_nr] = np.array([scale])
        else:
            nominal_scales[img_nr] = np.append(nominal_scales[img_nr], scale)

    # insert nominal diameters.
    # Assume that Images table is filled with basic info on images

    imgs_info = {}
    if scale_from_fits:
        # re-calculate scale from header info and scale factor
        for img_nr, scales in nominal_scales.items():
            res = database.execute(
                f"SELECT filename, asteroid_x, asteroid_y, asteroid_z, "
                f"earth_x, earth_y, earth_z "
                f"FROM Images WHERE id = {img_nr}")[0]
            filename = res[0]
            asteroid_pos = np.array(
                [float(res[1]), float(res[2]), float(res[3])])
            earth_pos = np.array([float(res[4]), float(res[5]), float(res[6])])

            # get Image's deg/px
            dpp = get_image_deg_per_pixel(filename)
            distance = np.linalg.norm(asteroid_pos - earth_pos) * AU_KM

            if img_nr not in imgs_info:
                imgs_info[img_nr] = {}
            imgs_info[img_nr]['dpp'] = dpp
            imgs_info[img_nr]['distance'] = distance

            radius = distance * np.tan(scales.mean()/2 * dpp * np.pi / 180.)
            deq = calculate_deq(volume_factor * volume_dimles, radius)

            database.execute(
                f"UPDATE Images SET deq_nominal = {deq} WHERE id == {img_nr} ")
            database.execute(
                f"UPDATE Images SET scale = {scales.mean()} WHERE id == {img_nr} ")
            database.execute(
                f"UPDATE Images SET radius_nominal = {radius} WHERE id == {img_nr} ")

    else:
        for img_nr, radiuses in nominal_radiuses.items():
            database.execute(
                f"UPDATE Images SET radius_nominal = {radiuses.mean()} "
                f"WHERE id == {img_nr} ")
            deq = calculate_deq(volume_factor * volume_dimles, radiuses.mean())

            database.execute(
                f"UPDATE Images SET deq_nominal = {deq} WHERE id == {img_nr} ")
            database.execute(
                f"UPDATE Images SET scale = {nominal_scales[img_nr].mean()} WHERE id == {img_nr} ")

    database.commit()
    return imgs_info


def calculate_clones_sizes(database, diameters_fn, scale_from_fits, imgs_info,
        volume_factor):
    # Now, do that for all of the clones
    radiuses_min = {}  # per image min radius
    radiuses_max = {}  # per image max radius
    deqs_min = {}  # per image min d_eq
    deqs_max = {}  # per image max d_eq

    f_diameters = open(diameters_fn, "r")
    # read line by line and calculate per image sizes
    count = 0
    while True:
        line = f_diameters.readline()
        if not line:
            break

        clone_id, volume_dimles, images_data = decompose_line(line)

        for data in images_data:
            img_nr = data['img_nr']
            radius = data['radius']
            rmsd = data['rmsd']
            scale = data['scale']

            if img_nr not in radiuses_min:
                radiuses_min[img_nr] = np.inf
            if img_nr not in radiuses_max:
                radiuses_max[img_nr] = -np.inf

            if img_nr not in deqs_min:
                deqs_min[img_nr] = np.inf
            if img_nr not in deqs_max:
                deqs_max[img_nr] = -np.inf

            deq = 0.0
            if scale_from_fits:
                radius = imgs_info[img_nr]['distance'] * \
                    np.tan(scale/2.0 *
                           imgs_info[img_nr]['dpp'] * np.pi / 180.)
                deq = calculate_deq(volume_factor * volume_dimles, radius)
            else:
                deq = calculate_deq(volume_factor * volume_dimles, radius)

            if radius < radiuses_min[img_nr]:
                radiuses_min[img_nr] = radius
            if radius > radiuses_max[img_nr]:
                radiuses_max[img_nr] = radius

            if deq < deqs_min[img_nr]:
                deqs_min[img_nr] = deq
            if deq > deqs_max[img_nr]:
                deqs_max[img_nr] = deq

        print(count, flush=True, end='\r')
        count += 1

    for img_nr, min_rad in radiuses_min.items():
        database.execute(
            f"UPDATE Images SET radius_min = {min_rad} WHERE id == {img_nr} ")
    for img_nr, max_rad in radiuses_max.items():
        database.execute(
            f"UPDATE Images SET radius_max = {max_rad} WHERE id == {img_nr} ")
    for img_nr, min_deq in deqs_min.items():
        database.execute(
            f"UPDATE Images SET deq_min = {min_deq} WHERE id == {img_nr} ")
    for img_nr, max_deq in deqs_max.items():
        database.execute(
            f"UPDATE Images SET deq_max = {max_deq} WHERE id == {img_nr} ")

    f_diameters.close()
    database.commit()


def calculate_sizes(database, diameters_fn, scale_from_fits, volume_factor=1.0):
    imgs_info = calculate_nominal_sizes(
        database, diameters_fn, scale_from_fits, volume_factor)
    calculate_clones_sizes(database, diameters_fn, scale_from_fits, imgs_info,
            volume_factor)
