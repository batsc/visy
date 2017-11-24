#!/usr/local/sci/bin/python2.7

# Generate an ortho projection plot of the UK + Europe from a slotstore
# for use in blender
#
# Specify timestamp on command line

import cartopy.crs as ccrs
import matplotlib.pyplot as plt
import h5py
import iris
from iris.coord_systems import Orthographic
from iris.coords import DimCoord
import numpy as np
import os
import sys
from SpsMod_Coordinates import GeoProjection

SATELLITE = "MSG_RSS"
SLOTSTORE_DIR = "/data/slotstores"
DEST_DIR = "/data/local/cbatston/blender"
apply_SEVIRI_grid_correction = True

LONS = {'MSG': 0.0, 'MSG_RSS': 9.5}
BLOCKS = {'MSG': 'U', 'MSG_RSS': 'L'}  # HRV blocks for UK area

try:
    ts = sys.argv[1]
except:
    print "Cannot get timestamp from args:" + str(sys.argv)
    sys.exit(1)

# Try find file
filein = SLOTSTORE_DIR + '/' + SATELLITE + '_' + ts + '.h5'

if not os.path.isfile(filein):
    print "File does not exist" + str(filein)
    sys.exit(1)

if not os.path.isdir(DEST_DIR):
    os.mkdir(DEST_DIR)

# Get HRV and IR data
try:
    h5 = h5py.File(filein, 'r')
    hrv = h5['MSG/HRV___/Refl'][:]
    ir = h5['MSG/IR_108/BT'][:]
    gi = h5['MSG/Prologue/GeneralInfo'][:]
    h5.close()
except:
    print "Could not get data from " + filein
    sys.exit(1)

# Define high and low resolution geostationary projections
gph = GeoProjection(SATELLITE, channel_resolution='HRV',
                    apply_SEVIRI_grid_correction=apply_SEVIRI_grid_correction)
gpl = GeoProjection(SATELLITE,
                    apply_SEVIRI_grid_correction=apply_SEVIRI_grid_correction)

# Get Iris cubes
hrv_c = gph.iris_cube(general_info=gi, HRV_block=BLOCKS[SATELLITE],
                      data=hrv)
ir_c = gpl.iris_cube(data=ir)


# Bounds of region to plot in Orthographic
plt_proj = ccrs.Orthographic(central_longitude=LONS[SATELLITE])
bl = [-30, 30]
tr = [60, 70]
br = [50, 30]
ortho_coords_bl = plt_proj.transform_point(bl[0], bl[1], ccrs.PlateCarree())
ortho_coords_tr = plt_proj.transform_point(tr[0], tr[1], ccrs.PlateCarree())
ortho_coords_br = plt_proj.transform_point(br[0], br[1], ccrs.PlateCarree())

# Plot details
dpi=100
image_width = 46

# Create ortho cube to regrid to
crs = Orthographic(0, LONS[SATELLITE])
x = np.linspace(ortho_coords_bl[0], ortho_coords_br[0], image_width * dpi)
xd = DimCoord(x, coord_system=crs, standard_name='projection_x_coordinate',
              units='m')
y = np.arange(ortho_coords_bl[1], ortho_coords_tr[1] + np.diff(x[:2]),
              np.diff(x[:2]))
yd = DimCoord(y, coord_system=crs, standard_name='projection_y_coordinate',
              units='m')
ortho_cube = iris.cube.Cube(data=np.zeros((y.size, x.size)))
ortho_cube.add_dim_coord(yd, 0)
ortho_cube.add_dim_coord(xd, 1)

hrv_o = hrv_c.regrid(ortho_cube, iris.analysis.Nearest())
ir_o = ir_c.regrid(ortho_cube, iris.analysis.Nearest())

# Set xlim, ylim
xlim = [hrv_o.coord('projection_x_coordinate').points.min(),
        hrv_o.coord('projection_x_coordinate').points.max()]
ylim = [hrv_o.coord('projection_y_coordinate').points.min(),
        hrv_o.coord('projection_y_coordinate').points.max()]
ratio = (np.diff(xlim)) / (np.diff(ylim))


figsize = [image_width, image_width / ratio]
extent = [xlim[0], xlim[1], 
          ylim[0], ylim[1]]

# HRV
fig = plt.figure(figsize=figsize, dpi=dpi, frameon=False)
ax = fig.add_axes([0,0,1,1], projection=plt_proj)
#ax.gridlines(xlocs=range(-80,81,10), ylocs=range(-80,81,10),
#             linewidth=3, color='b', linestyle='-')
ax.set_xlim(xlim)
ax.set_ylim(ylim)
#ax.coastlines('10m', color='r', linewidth=3)
ax.axis('off')
ax.imshow(hrv_o.data, vmin=0, vmax=1.2, cmap='gray', 
          interpolation='none', extent=extent)
fig.patch.set_visible(False)
plt.savefig(DEST_DIR + '/hrv_' + ts + '.png', transparent=True)

# IR
fig = plt.figure(figsize=figsize, dpi=dpi, frameon=False)
ax = fig.add_axes([0,0,1,1], projection=plt_proj)
ax.set_xlim(xlim)
ax.set_ylim(ylim)
ax.axis('off')
ax.imshow(ir_o.data, vmin=178, vmax=308, cmap='gray_r', 
          interpolation='none', extent=extent)
fig.patch.set_visible(False)
plt.savefig(DEST_DIR + '/ir_' + ts + '.png', transparent=True)

