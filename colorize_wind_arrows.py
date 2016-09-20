# -*- coding: iso-8859-1 -*-

from __future__ import division

import sys
import glob
import matplotlib.cm as cm
from matplotlib.colors import rgb2hex, Normalize
import matplotlib.pyplot as plt
from matplotlib.colorbar import ColorbarBase

indir = sys.argv[1]
outdir = sys.argv[2]

ms2mph = 2.2369362920544
index2ms = 0.514444 * 5

cmap = cm.gist_ncar
max_wind_index = 50
norm = Normalize(vmin=0, vmax=max_wind_index * index2ms * ms2mph)

svg_files = glob.glob(indir + '/WeatherSymbol_WMO_WindArrow*')

indices = []
winds = []
colors = []

for svg_file in svg_files:
    index = float(svg_file.rsplit('_', 1)[-1].rstrip('.svg'))
    if int(index) > max_wind_index:
        continue
    wind = index * index2ms
    color = rgb2hex(cmap(int(round(index * cmap.N / max_wind_index))))
    out_file = outdir + '/' + svg_file.rsplit('/')[-1]
    with open(svg_file, 'r') as infile, open(out_file, 'w') as outfile:
        line = infile.readline()
        while line:
            outfile.write(line)
            line = infile.readline()
            line = line.replace('#000000', str(color))
    indices.append(index)
    winds.append(wind)
    colors.append(color)

for (index, wind, color) in sorted(zip(indices, winds, colors)):
    print "{:2.0f} {:5.1f} {}".format(index, wind, color)

# Create an image showing the colorbar for the choosen colormap
fig = plt.figure(figsize=(1, 3.2), dpi=100)
ax = fig.add_axes([0.05, 0.05, 0.45, 0.9])
cb = ColorbarBase(ax, cmap=cmap, norm=norm, orientation='vertical')
cbytick_obj = plt.getp(cb.ax.axes, 'yticklabels')
plt.setp(cbytick_obj, fontsize=8)
cb.set_label('Wind speed (mph)', fontsize=9)
plt.savefig(outdir + '/amv_winds_key.png', transparent=True)

