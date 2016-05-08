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
import sys

channel_name_map = {'HRW_BASIC_CHANNEL00': 'SEVIRI Hi Res VIS',
                    'HRW_BASIC_CHANNEL02': 'SEVIRI VIS 0.8',
                    'HRW_BASIC_CHANNEL05': 'SEVIRI WV 6.2',
                    'HRW_BASIC_CHANNEL06': 'SEVIRI WV 7.0',
                    'HRW_BASIC_CHANNEL10': 'SEVIRI IR 12.0'}
coord_desc = ("longitude, latitude, height (not used), speed (m/s), " +
              "direction from (deg), pressure level (Pa)")

json_dict = {
             "type": "FeatureCollection",
             "features": []
             }

pr_bands = [(2e4, 4e4), (4e4, 6e4), (6e4, 8e4), (8e4, 10e4)]

infile = sys.argv[1]

# Get time from filename
data_time = datetime.datetime.strptime(re.search(r'\d{12}', infile).group(),
                                       '%Y%m%d%H%M')
h5 = h5py.File(infile)

# Loop over channels
for key, ds in h5.iteritems():

    # Loop over pressure bands
    for pr_limits in pr_bands:

        pr_desc = "{:.0f}-{:.0f} hPa".format(pr_limits[0] / 100, pr_limits[1] / 100)

        # Only keep winds in this pressure band and where conf >= 85
        keep = np.logical_and(ds['pressure'] >= pr_limits[0],
                                  ds['pressure'] < pr_limits[1],
                                  ds['conf_nwp'] >= 85)

        # Next loop iteration if there are no valid winds
        if keep.sum() == 0:
            continue

        # Define a regular grid, 0.5 deg resolution
        coords = np.vstack([ds['lon'][keep], ds['lat'][keep]]).T
        lons_reg = np.arange(coords[:, 0].min(), coords[:, 0].max(), 0.5)
        lats_reg = np.arange(coords[:, 1].min(), coords[:, 1].max(), 0.5)
        x, y = np.meshgrid(lons_reg, lats_reg)
        coords_interp = np.array([x.flatten(), y.flatten()]).T

        # KDTree for original coords
        k = scipy.spatial.ckdtree.cKDTree(coords)

        # Query using the interpolated coords. Set any coords greater
        # than a distance of 0.25 degrees away from a valid coord as the
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

        # Organise the data in order: lon, lat, z (not used but needed for
        # consistency with GeoJSON specification), speed, direction
        data = np.vstack([coords_interp[:,0], coords_interp[:,1],
                          np.zeros(spds.shape, dtype='int_'),
                          spds,
                          dirs.astype('int_')]).T

        # Round to 2 d.p.
        data = [[round(element, 2) for element in entry] for entry in data]

        # Define winds feature for this pressure band for this channel
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
