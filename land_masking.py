#!/usr/bin/python2.7

# Trying to determine whether a point is over land or not


import numpy as np
from shapely.geometry import Point
import cartopy.feature as cfeature

lons = np.linspace(-20, 20, 101)
lats = np.linspace(40, 60, 51)
lonsm, latsm = np.meshgrid(lons, lats)
coords = zip(lonsm.flatten(), latsm.flatten())
land_mask = np.zeros(lonsm.flatten().shape, dtype=bool)

land = cfeature.LAND
for idx, coord in enumerate(coords):
    for geom in land.geometries():
        if Point(coord).within(geom):
            land_mask[idx] = True

lonsm_masked = np.ma.array(lonsm, mask=land_mask)
latsm_masked = np.ma.array(latsm, mask=land_mask)

import cartopy.crs as ccrs
import matplotlib.pyplot as plt
ax = plt.axes(projection=ccrs.PlateCarree())
ax.coastlines()
ax.plot(lonsm_masked, latsm_masked, '.')
plt.show()
