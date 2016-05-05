#!/usr/local/sci/bin/python2.7
# -*- coding: iso-8859-1 -*-
# Plot winds from expanded domain

from __future__ import division
import h5py
import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import datetime
import iris
iris.FUTURE.strict_grib_load = True
import iris.plot as iplt

chan_map = {'HRW_BASIC_CHANNEL00': 'EVDN70',
            'HRW_BASIC_CHANNEL05': 'EWDA10',
            'HRW_BASIC_CHANNEL06': 'EWDA30',
            'HRW_BASIC_CHANNEL10': 'EIDA70'}

chan_name_map = {'HRW_BASIC_CHANNEL00': 'HRV',
                 'HRW_BASIC_CHANNEL05': 'WV6_2',
                 'HRW_BASIC_CHANNEL06': 'WV7',
                 'HRW_BASIC_CHANNEL10': 'IR12'}

plevels = {'high': (2e4, 4e4),
           'mid_high': (4e4, 6e4),
           'mid_low': (6e4, 8e4),
           'low': (8e4, 10e4)}

c_hi1 = np.array((214,   6,   6)) / 255
c_mh1 = np.array((  6,   6, 215)) / 255
c_ml1 = np.array((246, 181,   0)) / 255
c_lo1 = np.array((109, 212, 142)) / 255
c_hi2 = np.array((241,   2, 241)) / 255
c_mh2 = np.array((  2, 241, 241)) / 255
c_ml2 = np.array((238, 238,   2)) / 255
c_lo2 = np.array((  1, 245,   1)) / 255

color_map = {'high': {'HRW_BASIC_CHANNEL00': c_hi1,
                      'HRW_BASIC_CHANNEL10': c_hi2,
                      'HRW_BASIC_CHANNEL05': c_hi1,
                      'HRW_BASIC_CHANNEL06': c_hi2},
             'mid_high': {'HRW_BASIC_CHANNEL00': c_mh1,
                          'HRW_BASIC_CHANNEL10': c_mh2,
                          'HRW_BASIC_CHANNEL05': c_mh1,
                          'HRW_BASIC_CHANNEL06': c_mh2},
             'mid_low': {'HRW_BASIC_CHANNEL00': c_ml1,
                         'HRW_BASIC_CHANNEL10': c_ml2,
                         'HRW_BASIC_CHANNEL05': c_ml1,
                         'HRW_BASIC_CHANNEL06': c_ml2},
             'low': {'HRW_BASIC_CHANNEL00': c_lo1,
                     'HRW_BASIC_CHANNEL10': c_lo2,
                     'HRW_BASIC_CHANNEL05': c_lo1,
                     'HRW_BASIC_CHANNEL06': c_lo2}}

geo_prj = ccrs.Geostationary()
pc_prj = ccrs.PlateCarree()

def conv_wind_dir(angle):
    ''' Conv wind dir to trig representation
    '''
    a = 270 - angle
    a[a < 0] = a[a < 0] + 360
    return a

def set_up_plot(dest_prj):
    # Set up plot to show side by side wind barbs, for different levels
    # Bottom right, top left
    br = dest_prj.transform_point(27.29, 35.42, pc_prj)
    bl = dest_prj.transform_point(-30.66, 35.61, pc_prj)
    tl = dest_prj.transform_point(-57.81, 72.75, pc_prj)
    fig = plt.figure(figsize=(15.94, 5.84))
    ax = fig.add_axes([0,0,1,1], projection=dest_prj)
    ax.coastlines(resolution='50m', color='darkgray', zorder=1)
    ax.gridlines(color='darkgray')
    ax.set_xlim((bl[0], br[0]))
    ax.set_ylim((br[1], tl[1]))
    ax.outline_patch.set_visible(False)
    ax.background_patch.set_color('black')
    return (fig, ax)

def barb_values(w, k, plevs):
    # w = h5py fileobj, k = dataset channel
    # Return in Geostationary setup
    ve = (w[k]['wind_speed'] *
          np.cos(np.deg2rad(conv_wind_dir(w[k]['wind_direction']))))
    vn = (w[k]['wind_speed'] *
          np.sin(np.deg2rad(conv_wind_dir(w[k]['wind_direction']))))
    msk = np.logical_or(w[k]['pressure'] < plevs[0],
                        w[k]['pressure'] >= plevs[1])
    # Only plot every other one to thin out and make plot look better
    evens = np.arange(w[k]['pressure'].shape[0]) % 2 == 0
    msk = np.logical_or(msk, evens)
    u = np.ma.array(ve, mask=msk)
    v = np.ma.array(vn, mask=msk)
    pts = geo_prj.transform_points(pc_prj, np.ma.array(w[k]['lon'], mask=msk),
                                           np.ma.array(w[k]['lat'], mask=msk))
    x, y = pts[:, 0], pts[:, 1]
    return x, y, u, v

if __name__ == '__main__':

    nwcsaf_ts = datetime.datetime.strptime('201604270500', '%Y%m%d%H%M')
    auto_ts = nwcsaf_ts + datetime.timedelta(minutes=15)

    direc = '/net/home/h02/cbatston/tempstore/'
    fname = (direc + 'SAFNWC_MSG3_HRW__' + nwcsaf_ts.strftime('%Y%m%d%H%M') +
             '_europe______.buf.h5')

    # Load wind file
    w = h5py.File(fname)

    # Load GRIB file
    #g = iris.load_cube(direc + '/' + chan_map[chan] + '_' +
    #                   auto_ts.strftime('%Y%m%d%H%M') + '.grb')

    for levels in [['high', 'mid_high'], ['mid_low', 'low']]:
        for chans in [['HRW_BASIC_CHANNEL00', 'HRW_BASIC_CHANNEL10'],
                      ['HRW_BASIC_CHANNEL05', 'HRW_BASIC_CHANNEL06']]:
            fig, ax = set_up_plot(geo_prj)
            x_lim = ax.get_xlim()
            y_lim = ax.get_ylim()
            x_pos = (x_lim[0] + (x_lim[1] - x_lim[0]) * 0.01,
                     x_lim[0] + (x_lim[1] - x_lim[0]) * 0.13)
            y_pos = (y_lim[0] + (y_lim[1] - y_lim[0]) * 0.96,
                     y_lim[0] + (y_lim[1] - y_lim[0]) * 0.92)
            for xind, lev in enumerate(levels):
                for yind, chan in enumerate(chans):
                    x, y, u, v = barb_values(w, chan, plevels[lev])
                    ax.barbs(x, y, u, v, sizes=dict(emptybarb=0.005, spacing=0.15),
                             linewidth=0.45, length=5,
                             barbcolor=tuple(color_map[lev][chan]), zorder=2)
                    ax.text(x_pos[xind], y_pos[yind], chan_name_map[chan] +
                            " {:.0f}-{:.0f}hPa".format(plevels[lev][0] / 100, plevels[lev][1] / 100),
                            color=tuple(color_map[lev][chan]))
            fig.savefig('_'.join(('chan', levels[0], levels[1], chan_name_map[chans[0]],
                        chan_name_map[chans[1]])) + '_' + nwcsaf_ts.strftime('%Y%m%d%H%M') + '.png')


    #iplt.pcolormesh(g[::4, ::4], cmap='gray', vmin=0, vmax=1, zorder=0, alpha=0.5)



    w.close()
