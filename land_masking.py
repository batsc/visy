#!/usr/bin/python2.7
# -*- coding: iso-8859-1 -*-

# Trying to determine whether a point is over land or not

import iris
import numpy as np
from shapely.geometry import Point
import cartopy.feature as cfeature
import cPickle as pickle

file='/data/AutosatArchive/ImageArchive/MSG/XZ/20160113/ETXZ80_201601131000.ff'

cube = iris.load_cube(file)

# Set longitudes to -180 to 180
lons = cube.coord('longitude').points
lons[lons > 180.0] -= 360.0
cube.coord('longitude').points = lons
cube.coord('longitude').circular = False

cube.coord('longitude').guess_bounds()
cube.coord('latitude').guess_bounds()

lonsm, latsm = np.meshgrid(cube.coord('longitude').points,
                           cube.coord('latitude').points)
coords = zip(lonsm.flatten(), latsm.flatten())
land_mask = np.zeros(lonsm.flatten().shape, dtype=bool)

land = cfeature.LAND
for idx, coord in enumerate(coords):
    for geom in land.geometries():
        if Point(coord).within(geom):
            land_mask[idx] = True

land_mask = land_mask.reshape(cube.coord('latitude').points.shape,
                              cube.coord('longitude').points.shape)

# Save land mask
pickle.dump(land_mask, '/home/h02/cbatston/Work/2013_08_01_WAFC_products/' +
                       'ATD_CB_link_analysis/land_mask_wafc.p')
