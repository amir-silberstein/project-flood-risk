# -*- coding: utf-8 -*-
"""
Data and Plotting Script — Project Flood Risk Module 5
Includes Interactive Coordinate Picker
"""

from pathlib import Path
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.colors import LinearSegmentedColormap

# ==============================================================================
# 1. SETUP & CONFIGURATION
# ==============================================================================
try:
    SCRIPT_DIR = Path(__file__).parent
except NameError:
    SCRIPT_DIR = Path.cwd()

mpl.rcParams['savefig.dpi'] = 300
mpl.rcParams['figure.dpi'] = 100

yrange = np.arange(0, 223, 1)
xrange = np.arange(0, 983, 1)
compartment = np.zeros((223, 983))

# ==============================================================================
# 2. LOADING DATA
# ==============================================================================
dikeringarea = pd.read_csv(
    SCRIPT_DIR / 'Dikeringarea.txt', header=None, delimiter=';'
).to_numpy()
inhabitants = pd.read_csv(
    SCRIPT_DIR / 'Inhabitants.txt', header=None, delimiter=';'
).to_numpy()
landuse = pd.read_csv(
    SCRIPT_DIR / 'landuse.txt', header=None, delimiter=';'
).to_numpy()
AHN_max = pd.read_csv(
    SCRIPT_DIR / 'AHN_max.txt', header=None, delimiter=';'
).to_numpy()
AHN_gem = pd.read_csv(
    SCRIPT_DIR / 'AHN_avg.txt', header=None, delimiter=';'
).to_numpy()

# ==============================================================================
# 3. HIGH-ACCURACY ELEVATION MAP WITH INTERACTIVE CLICK PICKER
# ==============================================================================
fig, ax = plt.subplots(figsize=(12, 5))
plt.title(
    'Maximum Elevation [m+NAP] — Click Anywhere to Print Coordinates',
    fontsize=11,
    weight='bold',
)

# Height Calibration
vmin_elev = float(np.floor(np.nanmin(AHN_max)))
vmax_elev = float(np.ceil(np.nanpercentile(AHN_max, 98)))

levels = np.arange(vmin_elev, vmax_elev + 0.5, 0.5)

# Modern Matplotlib colormap resampling syntax
cmap_elev = mpl.colormaps['terrain'].resampled(len(levels) - 1)
norm_elev = mpl.colors.BoundaryNorm(levels, cmap_elev.N)

# Plot array
im = ax.imshow(
    AHN_max,
    cmap=cmap_elev,
    norm=norm_elev,
    origin='lower',
    extent=[0, 983, 0, 223],
    aspect='equal',
)

# Colorbar
cb = fig.colorbar(
    im,
    ax=ax,
    shrink=0.85,
    pad=0.02,
    ticks=np.arange(vmin_elev, vmax_elev + 1, 1),
)
cb.set_label('Elevation [m + NAP]', fontsize=10)

# Coordinate Grid
ax.set_xticks(np.arange(0, 984, 50))
ax.set_xticks(np.arange(0, 984, 10), minor=True)
ax.set_yticks(np.arange(0, 224, 25))
ax.set_yticks(np.arange(0, 224, 5), minor=True)

ax.grid(
    True, which='major', color='black', linestyle='-', linewidth=0.5, alpha=0.6
)
ax.grid(
    True, which='minor', color='gray', linestyle=':', linewidth=0.3, alpha=0.5
)

# Boundary lines
ax.plot([150, 150], [0, 223], color='black', linewidth=1.5)
ax.plot([400, 550], [223, 0], color='blue', linewidth=1.5)
ax.plot([700, 800], [0, 223], color='red', linewidth=1.5)
ax.plot([150, 345], [100, 100], color='green', linewidth=1.5)

ax.set_xlabel('ix (Cell X Coordinate: 0 to 983)', fontsize=10)
ax.set_ylabel('iy (Cell Y Coordinate: 0 to 223)', fontsize=10)
ax.set_xlim(0, 983)
ax.set_ylim(0, 223)
plt.tight_layout()

# --- Interactive Click Event Function ---
clicked_marker = None

def onclick(event):
    global clicked_marker
    if event.inaxes == ax and event.xdata is not None and event.ydata is not None:
        ix = int(np.clip(round(event.xdata), 0, 982))
        iy = int(np.clip(round(event.ydata), 0, 222))
        elevation = AHN_max[iy, ix]

        print(
            f"--> Clicked Location: ix={ix}, iy={iy} | Elevation={elevation:.2f} m+NAP"
        )

        # Draw/update a small red marker where clicked
        if clicked_marker is not None:
            clicked_marker.remove()
        (clicked_marker,) = ax.plot(ix, iy, 'ro', markersize=6, markeredgecolor='black')
        fig.canvas.draw_idle()

# Connect mouse click handler to canvas
fig.canvas.mpl_connect('button_press_event', onclick)

# ==============================================================================
# 4. DIKE RING AREAS MAP
# ==============================================================================
fig2, ax2 = plt.subplots(figsize=(10, 4.5))
plt.title('Dike Ring Areas', fontsize=11, weight='bold')

ax2.imshow(dikeringarea, cmap='jet', origin='lower', extent=[0, 983, 0, 223])
plt.text(150, 75, '16', fontsize=18, color='white', weight='bold')
plt.text(550, 125, '43', fontsize=18, color='white', weight='bold')

ax2.axis('scaled')
ax2.set_xlabel('ix (100m)')
ax2.set_ylabel('iy (100m)')

# ==============================================================================
# 5. COMPARTMENT DEFINITION & PLOTTING
# ==============================================================================
for iy in yrange:
    for ix in xrange:
        if np.isnan(dikeringarea[iy, ix]):
            compartment[iy, ix] = np.nan
        elif dikeringarea[iy, ix] == 43:
            if iy > 223 * (800 - ix) / 100:
                compartment[iy, ix] = 1
            elif iy > 223 * (ix - 400) / 150:
                compartment[iy, ix] = 2
            else:
                compartment[iy, ix] = 3
        elif dikeringarea[iy, ix] == 16:
            if ix > 150:
                if iy > 100:
                    compartment[iy, ix] = 4
                else:
                    compartment[iy, ix] = 5
            else:
                compartment[iy, ix] = 6

fig3, ax3 = plt.subplots(figsize=(10, 4.5))
plt.title('Compartments', fontsize=11, weight='bold')

colors_comp = [
    (1, 1, 1),
    (1, 0, 0),
    (1, 1, 0),
    (0, 0, 1),
    (1, 0, 1),
    (0.3, 1, 0.2),
    (0, 1, 1),
]
cmap_comp = LinearSegmentedColormap.from_list('my_list', colors_comp)
norm_comp = mpl.colors.BoundaryNorm(range(8), cmap_comp.N)

ax3.imshow(
    compartment,
    cmap=cmap_comp,
    norm=norm_comp,
    origin='lower',
    extent=[0, 983, 0, 223],
)

plt.text(825, 125, '1', fontsize=18, color='black', weight='bold')
plt.text(575, 125, '2', fontsize=18, color='black', weight='bold')
plt.text(400, 100, '3', fontsize=18, color='white', weight='bold')
plt.text(300, 150, '4', fontsize=18, color='black', weight='bold')
plt.text(200, 50, '5', fontsize=18, color='black', weight='bold')
plt.text(75, 50, '6', fontsize=18, color='black', weight='bold')

ax3.axis('scaled')
ax3.set_xlabel('ix (100m)')
ax3.set_ylabel('iy (100m)')

plt.show()