
import cartopy.crs as ccrs
import matplotlib.pyplot as plt
import iris
from iris.coord_systems import Orthographic
from iris.coords import DimCoord
import numpy as np

vis = iris.load_cube('/home/batsc/python/cartopy/EVDN70_201710131130.grb')

# Bounds of region to plot in Orthographic
plt_proj = ccrs.Orthographic(central_longitude=9.5)
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
crs = Orthographic(0, 9.5)
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

data = vis.regrid(ortho_cube, iris.analysis.Nearest())

# Set xlim, ylim
xlim = [data.coord('projection_x_coordinate').points.min(),
        data.coord('projection_x_coordinate').points.max()]
ylim = [data.coord('projection_y_coordinate').points.min(),
        data.coord('projection_y_coordinate').points.max()]
ratio = (np.diff(xlim)) / (np.diff(ylim))


figsize = [image_width, image_width / ratio]
#figsize = [image_width*0.3, image_width*0.3 / ratio]
extent = [xlim[0], xlim[1], 
          ylim[0], ylim[1]]

fig = plt.figure(figsize=figsize, dpi=dpi, frameon=False)
ax = fig.add_axes([0,0,1,1], projection=plt_proj)
#ax.gridlines(xlocs=range(-80,81,10), ylocs=range(-80,81,10),
#             linewidth=3, color='b', linestyle='-')
ax.set_xlim(xlim)
ax.set_ylim(ylim)
#ax.coastlines('10m', color='r', linewidth=3)
ax.axis('off')
ax.imshow(data.data, vmin=0, vmax=1.2, cmap='gray', 
          interpolation='none', extent=extent)
fig.patch.set_visible(False)
plt.savefig('vis.png', transparent=True)

