# AO_SIZE analysis

Set of scripts to analyse the results of `aosize` (fitting clones to the ao
Images)

# Usage

Execute scripts in order:

```bash
./create_db.py --db-name EXAMPLE.DB
./insert_model.py --db-name example.db [--obj MODEL.OBJ] [--inp INP] [--param PARAM]
./insert_images.py --db-name EXAMPLE.DB --img-list IMG_LIST --img-dir IMG_DIR [-c]
./calculate_sizes.py --db-name EXAMPLE.DB --diameters DIAMETERS.DAT
```

`IMG_LIST` is a file with the list of ao images in a format:

```
id filename.fits jd something ax ay az ex ey ez
```

`ax, ...` is the position of the target (in AU), `ex, ...` - earth position.

`IMG_DIR` points to the folder containing imiges.


# Database

## Model

Holds information on the model

```
filename TEXT, target TEXT, method TEXT, period DOUBLE, lambda DOUBLE, beta DOUBLE, gamma DOUBLE, jd_g0 DOUBLE
```

## Images

Table with per image info, constructed from `diameters.dat`

```
id INTEGER PRIMARY KEY, deq_min DOUBLE, deq_max DOUBLE, deq_nominal DOUBLE, radius_min DOUBLE, radius_max DOUBLE, radius_nominal DOUBLE, jd DOUBLE, asteroid_x DOUBLE, asteroid_y DOUBLE, asteroid_z DOUBLE, earth_x DOUBLE, earth_y DOUBLE, earth_z DOUBLE, aspect DOUBLE, phase DOUBLE, kmppx DOUBLE, filename TEXT
```



