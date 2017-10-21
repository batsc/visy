
import cartopy
import cartopy.crs as ccrs
import matplotlib.pyplot as plt
import iris
import numpy as np

vis = iris.load_cube('/home/batsc/python/cartopy/EVDN70_201710131130.grb')

# Bounds of region to plot in geo proj
plt_proj = ccrs.Geostationary()
coords_bl = plt_proj.transform_point(-30, 40, ccrs.PlateCarree())
coords_tr = plt_proj.transform_point(48, 70, ccrs.PlateCarree())

# Plot details
dpi=100
image_width = 28

con_x0 = iris.Constraint(projection_x_coordinate=lambda x: x >= coords_bl[0])
con_x1 = iris.Constraint(projection_x_coordinate=lambda x: x <= coords_tr[0])
con_y0 = iris.Constraint(projection_y_coordinate=lambda y: y >= coords_bl[1])
con_y1 = iris.Constraint(projection_y_coordinate=lambda y: y <= coords_tr[1])
vis_sm = vis.extract(con_x0 & con_y0 & con_x1 & con_y1)

# Set xlim, ylim
xlim = [vis_sm.coord('projection_x_coordinate').points.min(),
        vis_sm.coord('projection_x_coordinate').points.max()]
ylim = [vis_sm.coord('projection_y_coordinate').points.min(),
        vis_sm.coord('projection_y_coordinate').points.max()]
ratio = (np.diff(xlim)) / (np.diff(ylim))

figsize = [image_width, image_width / ratio]
#figsize = [image_width * 0.3, image_width * 0.3 / ratio]
extent = [xlim[0], xlim[1], 
          ylim[0], ylim[1]]

fig = plt.figure(figsize=figsize, dpi=dpi, frameon=False)
ax = fig.add_axes([0,0,1,1], projection=plt_proj)
ax.gridlines(xlocs=range(-80, 81, 10), ylocs=range(-80, 81, 10),
             linewidth=3, color='b', linestyle='-')
ax.set_xlim(xlim)
ax.set_ylim(ylim)
ax.coastlines('10m', color='r',linewidth=3)
ax.axis('off')
#ax.imshow(vis_sm.data[:, ::-1], vmin=0, vmax=1, cmap='gray', 
#          interpolation='none', extent=extent)
fig.patch.set_visible(False)
plt.savefig('coasts.png', transparent=True)

