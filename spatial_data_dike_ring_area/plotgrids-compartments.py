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
        - For operations summarizing data (sum, max, min for example), Python 
        has specific NaN versions (nansum, nanmax, ...) ignoring NaN values;
        alterantively, an if-loop can be used of course
"""

import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.patches import Patch

mpl.rcParams['savefig.dpi'] = 1000
mpl.rcParams['figure.dpi'] = 300

""" defining data dimensions 
    (note that in python definitions matriy dimensions come with the 
     x-dinension second and the y-dimension first: this may confuse) """
dikeringarea = np.zeros((223,983))
compartment = np.zeros((223,983))
inhabitants = np.zeros((223,983))
landuse = np.zeros((223,983))
AHN_max = np.zeros((223,983))
AHN_avg = np.zeros((223,983))

yrange = np.arange(0,223,1)
xrange = np.arange(0,983,1)


""" Loading data """
dikeringarea = pd.read_csv('Dikeringarea.txt',header=None, 
                           delimiter = ';').to_numpy()
inhabitants = pd.read_csv('Inhabitants.txt',header=None, 
                          delimiter = ';').to_numpy()
landuse = pd.read_csv('landuse.txt',header=None, 
                      delimiter = ';').to_numpy()
AHN_max = pd.read_csv('AHN_max.txt', header = None, delimiter = ';').to_numpy()
AHN_gem = pd.read_csv('AHN_avg.txt', header = None, delimiter = ';').to_numpy()

"""
# aggregate inhabitants over the cells (ignoring NaNs of cells outside the area)
print('Population: \nTotal population: ' + str(np.nansum(inhabitants)))

# Determine land-use classes
# Initialization of land-use classes matriy: 9x1
# Filling of land-use classes matriy. For loop trough all boxes
lu_class_area = np.zeros((9,1))
for iy in yrange:
    for ix in xrange:
       if ~np.isnan(landuse[iy,ix]):
           lu_class_area[int(landuse[iy,ix])-1,0] = lu_class_area[int(landuse[iy,ix])-1,0] + 0.01
           # Each cell adds 1 ha, or 0.01 km2 to the total area of its land-use class

print('\nLanduse:')    
print(pd.DataFrame(data=lu_class_area,index=["Infrastructure","Residential","Industry/commercial","Governmental institutions/services","Recreation","Greenhouses","Agriculture","Water","Nature"],columns = ["Area (km2)"]))           

# Change land-use matriy
for iy in yrange:
    for ix in xrange:
        if np.isnan(landuse[iy,ix]):
            landuse[iy,ix] = 0
landuse = landuse.astype(int)

# Plotting - Examples
# Plotting of data allows a direct first visual verification!
# Plot the land-use
fig,ax = plt.subplots()
plt.title('Land Use Classes')
colors9 = [(0.,0.,0.),(1.0,0.0,0.0),(1.0,0.0,1.0),(0.6,0.6,0.0),
          (1.0,1.0,0.0),(0.0,0.0,1.0),(0.3,1.0,0.2),(0.0,1.0,1.0),
          (0.1,0.4,0.1)]
colors = [(1,1,1)]+colors9
colormap_landuse = LinearSegmentedColormap.from_list("my_list",colors)
cmap = colormap_landuse
bounds = [0,1,2,3,4,5,6,7,8,9,10]
labels = ["Infrastructure","Residential","Industry","Services","Recreation",
          "Greenhouses","Agriculture","Water","Nature"]
len_lab = len(labels)
legend_elements = [Patch(facecolor=color, edgecolor='w') for color in colors9]
norm = mpl.colors.BoundaryNorm(bounds,cmap.N)
box = ax.get_position()
ax.set_position([box.x0, box.y0, box.width*0.8, box.height])
ax.legend(handles=legend_elements,labels=labels,loc="center left",
          fontsize='xx-small',bbox_to_anchor=(1,0.5))
p1 = plt.pcolor(np.flipud(landuse),cmap=cmap,norm=norm)

#ax.axis('equal')
ax.axis('scaled')
ax.set_xlabel('x (100m)')
ax.set_ylabel('y (100m)')
"""

# Plot the maximum elevation
fig,ax = plt.subplots()
plt.title('Maximum elevation [m+NAP]')
p2 = plt.pcolor(np.flipud(AHN_max),cmap='jet')
cb = fig.colorbar(p2,shrink=0.4,ticks=[0,5,10,15,20,25])

# possible compartment separation through (150,0) and (150,223)
# line: ix = 150
#
# This is not a plausible boundary of the compartments, but serves as example
#
# You can choose / find appropriate separating lines, quite close to the actual
# curved boundaries of compartments. More advanced approaches are possible.
#
# note: plot call format uses [x1, x2],[y1, y2]  
#                             (and not reversed order as in natrix)
plt.plot([150, 150], [0, 223], color='black')

# possible compartment separation through (400,223) and (550,0)
# line: iy = 223*(550 - ix)/150
plt.plot([400, 550], [223, 0], color='blue')

# possible compartment separation through (700,0) and (800,223)
# line: iy = 223*(ix - 700)/100
plt.plot([700, 800], [0, 223], color='red')

# possible compartment separation through (150,100) and (345,100)
# line: iy = 223*(ix - 700)/100
plt.plot([150, 345], [100, 100], color='green')

# note: text call format uses x,y (and not reversed order s in matrix) 
plt.text(570,25,"less plausible lines as\ncompartment boundaries", 
         fontsize=5, color='black', backgroundcolor='white')

ax.axis('scaled')
ax.set_xlabel('x (100m)')
ax.set_ylabel('y (100m)')

"""
# Plot the average elevation
fig,ax = plt.subplots()
plt.title('Average elevation [m+NAP]')
p3 = plt.pcolor(np.flipud(AHN_gem),cmap='jet')
cb = fig.colorbar(p3,shrink=0.4,ticks=[0,5,10,15,20,25])
ax.axis('scaled')
ax.set_xlabel('x (100m)')
ax.set_ylabel('y (100m)')

# Plot population per hectare
fig,ax = plt.subplots()
plt.title('Population per hectare (10log)')

# Convert to 10log scale for better interpretability
inhabitants_new = np.empty((223,983))
for iy  in yrange:
    for ix in xrange:
        if inhabitants[iy,ix] > 0:
            inhabitants_new[iy,ix] = np.log10(inhabitants[iy,ix])
        if inhabitants_new[iy,ix] == 0:
            inhabitants_new[iy,ix] = np.nan
p4 = plt.pcolor(np.flipud(inhabitants_new),cmap='hsv')
cb = fig.colorbar(p4,shrink=0.4)
ax.axis('scaled')
ax.set_xlabel('x (100m)')
ax.set_ylabel('y (100m)')
"""

# Plot the dike-ring area
fig,ax = plt.subplots()
plt.title('Dike ring areas')
p5 = plt.pcolor(np.flipud(dikeringarea),cmap='jet')

# note: text call format uses x,y (and not reversed order s in matrix) 
plt.text(150,75,"16",fontsize=20,color='white')
plt.text(550,125,"43",fontsize=20,color='white')

ax.axis('scaled')
ax.set_xlabel('x (100m)')
ax.set_ylabel('y (100m)')

# define compartments
for iy in yrange:
    for ix in xrange:
        if np.isnan(dikeringarea[iy,ix]):
            compartment[iy,ix] = np.nan
                   
        if dikeringarea[iy,ix] == 43:
            if iy > 223*(800-ix)/100:
                compartment[iy,ix] = 1
            else:
                if iy > 223*(ix-400)/150:
                    compartment[iy,ix] = 2
                else:
                    compartment[iy,ix] = 3
            
        else:
            if dikeringarea[iy,ix] == 16:
                if ix > 150:
                    if iy > 100:
                        compartment[iy,ix] = 4
                    else:
                        compartment[iy,ix] = 5
                else:
                    compartment[iy,ix] = 6

# Plot the compartments
fig,ax = plt.subplots()
compartment_class = np.zeros((6,1))
colors = [(1,1,1),(1,0,0),(1,1,0),(0,0,1),(1,0,1),(0.3,1,0.2),(0,1,1)]
colormap_landuse = LinearSegmentedColormap.from_list("my_list",colors)
cmap = colormap_landuse
bounds = [0,1,2,3,4,5,6,7]
norm = mpl.colors.BoundaryNorm(bounds,cmap.N)
p6 = plt.pcolor(np.flipud(compartment),cmap=cmap,norm=norm)
# note: text call format uses x,y (and not reversed order s in matrix) 
plt.text(825,125,"1",fontsize=20,color='black')
plt.text(575,125,"2",fontsize=20,color='black')
plt.text(400,100,"3",fontsize=20,color='white')
plt.text(300,150,"4",fontsize=20,color='black')
plt.text(200,50,"5",fontsize=20,color='black')
plt.text(75,50,"6",fontsize=20,color='black')
plt.text(570,25,"less plausible lines as\ncompartment boundaries", 
         fontsize=6, color='black')
plt.title('Compartments')
ax.axis('scaled')
ax.set_xlabel('x (100m)')
ax.set_ylabel('y (100m)')