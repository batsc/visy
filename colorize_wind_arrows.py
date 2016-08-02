
from __future__ import division

import sys
import glob
import matplotlib.cm as cm
from matplotlib.colors import rgb2hex

indir = sys.argv[1]
outdir = sys.argv[2]

cmap = cm.jet

max_wind_index = 50

svg_files = glob.glob(indir + '/WeatherSymbol_WMO_WindArrow*')

for svg_file in svg_files[:3]:
    index = float(svg_file.rsplit('_', 1)[-1].rstrip('.svg'))
#    wind = index * 0.514444 * 5
    color = rgb2hex(cmap(int(round(index * cmap.N / max_wind_index))))
    out_file = outdir + '/' + svg_file.rsplit('/')[-1]
    with open(svg_file, 'r') as infile, open(out_file, 'w') as outfile:
        line = infile.readline()
        while line:
            outfile.write(line)
            line = infile.readline()
            line = line.replace('#000000', str(color))
