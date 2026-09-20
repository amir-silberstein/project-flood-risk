# -*- coding: utf-8 -*-
"""
Data and plot Project Flood Risk Module 5

Data:
    Dike-ring-area: 100x100m raster where cell values 16, 43 denote dike ring 
    areas 16 and 43
    Land-use: 100x100m raster, cell value denotes the dominant land use
        Source: BBG2008 (CBS) and BRP2009 (Ministery of Economic Affairs)
        Land-use classes:
            1. Infrastructure
            2. Residential
            3. Industry/commercial
            4. Governmental institutions / services
            5. Recreation
            6. Greenhouses
            7. Agriculture
            8. Water
            9. Nature
    Inhabitants: 100x100m raster, cell value denotes number of inhabitants
        Source: CBS (2013)
    AHN: Actueel Hoogtebestand Nederland: digital elevation raster, 5x5m, 
    aggregated to 100x100m cells in two manners:
        AHN_max: Cell value is the maximum elevation in the 100x100m cell
        AHN_gem: Ceel value is the average elevation in the 100x100m cell

    Note that all rasters contain NaN (not a number) values outside the area 
    of dike rings 16 and 43. 
        - In making grid based calculations, operations with NaN input will 
        always result in NaN output.
        - For operations summarizing data (sum, max, min for example), Python has 
        specific NaN versions (nansum, nanmax, ...) avoiding NaN output
"""
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LinearSegmentedColormap
from pathlib import Path


output_dir = Path(__file__).resolve().parent / 'python_output'
output_dir.mkdir(exist_ok=True)


""" Loading data """
dikeringarea = pd.read_csv('Dikeringarea.txt',header=None, delimiter = ';').to_numpy()
inhabitants = pd.read_csv('Inhabitants.txt',header=None, delimiter = ';').to_numpy()
landuse = pd.read_csv('Landuse.txt',header=None, delimiter = ';').to_numpy()
AHN_max = pd.read_csv('AHN_max.txt', header = None, delimiter = ';').to_numpy()
AHN_gem = pd.read_csv('AHN_avg.txt', header = None, delimiter = ';').to_numpy()

print('Population: \nTotal population: ' + str(np.nansum(inhabitants)))

""" Determine land-use classes"""
# Initialization of land-use classes matrix: 9x1
# Filling of land-use classes matrix. For loop trough all boxes
lu_class_area = np.zeros((9,1))
xrange = np.arange(0,223,1)
yrange = np.arange(0,983,1)
for ix in xrange:
    for iy in yrange:
       if ~np.isnan(landuse[ix,iy]):
           lu_class_area[int(landuse[ix,iy])-1,0] = lu_class_area[int(landuse[ix,iy])-1,0] + 0.01
           # Each cell adds 1 ha, or 0.01 km2 to its land-use class

print('\nLanduse:')    
print(pd.DataFrame(data=lu_class_area,index=["Infrastructure","Residential","Industry/commercial","Governmental institutions/services","Recreation","Greenhouses","Agriculture","Water","Nature"],columns = ["Area (km2)"]))           

# Change land-use matrix
for ix in xrange:
    for iy in yrange:
        if np.isnan(landuse[ix,iy]):
            landuse[ix,iy] = 0
landuse = landuse.astype(int)

""" Plotting - Examples """ 
""" Plotting of data allows a direct first visual verification!"""
# Plot the land-use
fig,ax = plt.subplots()
plt.title('Land Use Classes')
colors = [(1,1,1),(0.0,0.0,0.0),(1.0,0.0,0.0),(1.0,0.0,1.0),(0.6,0.6,0.0),(1.0,1.0,0.0),(0.0,0.0,1.0),(0.3,1.0,0.2),(0.0,1.0,1.0),(0.1,0.4,0.1)]
colormap_landuse = LinearSegmentedColormap.from_list("my_list",colors)
cmap = colormap_landuse
bounds = [0,1,2,3,4,5,6,7,8,9,10]
norm = mpl.colors.BoundaryNorm(bounds,cmap.N)
p1 = plt.pcolor(np.flipud(landuse),cmap=cmap,norm=norm)
cb = fig.colorbar(p1,spacing='uniform')

#ax.axis('equal')
ax.axis('scaled')
ax.set_xlabel('x (100m)')
ax.set_ylabel('y (100m)')
fig.savefig(output_dir / 'land_use_classes.png', bbox_inches='tight')

# Plot the maximum elevation
fig,ax = plt.subplots()
plt.title('Maximum elevation [m+NAP]')
p2 = plt.pcolor(np.flipud(AHN_max),cmap='jet')
cb = fig.colorbar(p2)
ax.axis('scaled')
ax.set_xlabel('x (100m)')
ax.set_ylabel('y (100m)')
fig.savefig(output_dir / 'maximum_elevation.png', bbox_inches='tight')

# Plot the average elevation
fig,ax = plt.subplots()
plt.title('Average elevation [m+NAP]')
p3 = plt.pcolor(np.flipud(AHN_gem),cmap='jet')
cb = fig.colorbar(p3)
ax.axis('scaled')
ax.set_xlabel('x (100m)')
ax.set_ylabel('y (100m)')
fig.savefig(output_dir / 'average_elevation.png', bbox_inches='tight')

# Plot population per hectare
fig,ax = plt.subplots()
plt.title('Population per hectare (10log)')

# Adapt to 10log scale
inhabitants_new = np.full(inhabitants.shape, np.nan)
for ix  in xrange:
    for iy in yrange:
        if inhabitants[ix,iy] > 0:
            inhabitants_new[ix,iy] = np.log10(inhabitants[ix,iy])
p4 = plt.pcolor(np.flipud(inhabitants_new),cmap='hsv')
cb = fig.colorbar(p4)
ax.axis('scaled')
ax.set_xlabel('x (100m)')
ax.set_ylabel('y (100m)')
fig.savefig(output_dir / 'population_per_hectare_log10.png', bbox_inches='tight')

plt.show()