#!/usr/local/sci/bin/python2.7

# Modules
from __future__ import division
import datetime
import h5py
import json
import numpy as np
import re
import scipy.interpolate
import scipy.spatial.ckdtree

channel_name_map = {'HRW_BASIC_CHANNEL00': 'SEVIRI Hi Res VIS',
                    'HRW_BASIC_CHANNEL05': 'SEVIRI WV 6.2',
                    'HRW_BASIC_CHANNEL06': 'SEVIRI WV 7.0',
                    'HRW_BASIC_CHANNEL10': 'SEVIRI IR 12.0'}
coord_desc = ("longitude, latitude, height (not used), speed (m/s), " +
              "direction from (deg), pressure level (Pa)")

json_dict = {
             "type": "FeatureCollection",
             "features": []
             }

# HOW CAN WE THIN THE NUMBER OF WINDS (reduce neighbours)

# Load in winds from h5 file - need lat/lon/spd/direc/conf
#  and ignore values where conf < 85

# Output to GeoJSON format. Each feature would be a MultiPoint
#  and each feature represents winds from a channel for a specific
#  level (pressure band)

infile='SAFNWC_MSG3_HRW__201605050900_europe______.buf.h5'

# Get time from filename
data_time = datetime.datetime.strptime(re.search(r'\d{12}', infile).group(),
                                       '%Y%m%d%H%M')
h5 = h5py.File(infile)

# Loop over channels
#for ds in h5.values():

key = 'HRW_BASIC_CHANNEL10'
ds = h5[key]

pr_bands = [(2e4, 4e4), (4e4, 6e4), (6e4, 8e4), (8e4, 10e4)]

#for pr_limits in pr_bands:
pr_limits = pr_bands[0]

pr_desc = "{:.0f}-{:.0f} hPa".format(pr_limits[0] / 100, pr_limits[1] / 100)

# Only keep winds in this pressure band and where conf >= 85
keep = np.logical_and(ds['pressure'] >= pr_limits[0],
                          ds['pressure'] < pr_limits[1],
                          ds['conf_nwp'] >= 85)

# Define a regular grid, 0.1 deg resolution
coords = np.vstack([ds['lon'][keep], ds['lat'][keep]]).T
#lons_reg = np.arange(coords[:, 0].min(), coords[:, 0].max(), 0.1)
#lats_reg = np.arange(coords[:, 1].min(), coords[:, 1].max(), 0.1)
lons_reg = np.arange(coords[:, 0].min(), coords[:, 0].max(), 0.5)
lats_reg = np.arange(coords[:, 1].min(), coords[:, 1].max(), 0.5)
x, y = np.meshgrid(lons_reg, lats_reg)
coords_interp = np.array([x.flatten(), y.flatten()]).T

# KDTree for original coords
k = scipy.spatial.ckdtree.cKDTree(coords)

# Query using the interpolated coords. Set any coords greater
# than a distance of 0.5 degrees away from a valid coord as the
# null flag (i.e. i = coords.shape[0]).
d, i = k.query(coords_interp, distance_upper_bound=0.25)

# Keep only the valid interpolated coords
coords_interp = coords_interp[i < coords.shape[0], :]

# Create nearest neighbour interpolaters
spd = ds['wind_speed'][keep]
direc = ds['wind_direction'][keep]
spd_NNI = scipy.interpolate.NearestNDInterpolator(coords, spd)
dir_NNI = scipy.interpolate.NearestNDInterpolator(coords, direc)

# Get the NN values for the interpolated coordinates
spds = spd_NNI.__call__(coords_interp)
dirs = dir_NNI.__call__(coords_interp)

data = np.vstack([coords_interp[:,0], coords_interp[:,1],
                  np.zeros(spds.shape, dtype='int_'),
                  spds,
                  dirs.astype('int_')]).T


# Organise the data in order: lon, lat, z (not used but needed for
# consistency with GeoJSON specification), speed, direction
# Round to 2 d.p.
data = np.vstack([ds['lon'][keep], ds['lat'][keep],
                  np.zeros(ds['lon'][keep].shape, dtype='int_'),
                  ds['wind_speed'][keep],
                  ds['wind_direction'][keep].astype('int_')]).T
data = data.tolist()
# NEED to figure out how to remove redundant '.0's in json file
data = [[round(element, 2) for element in entry] for entry in data]

winds = {
         "type": "Feature",
         "geometry": {
                      "type": "MultiPoint",
                      "coordinates": data
                      },
         "properties": {
                        "name": channel_name_map[key],
                        "pressure_levels": pr_desc,
                        "coordinates_description": coord_desc
                        }
         }

json_dict["features"].append(winds)

outfile = 'test4.json'
with open(outfile, "w") as text_file:
    text_file.write(json.dumps(json_dict, separators=(',', ':')))

h5.close()
