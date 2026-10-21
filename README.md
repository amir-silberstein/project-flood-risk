# Flood Risk Model

The model runs in stages:

1. **Hydrological** (`modules/hydrological/`)  
   Converts return periods and river discharges into water levels and breach discharges.

2. **Dike** (`modules/dike/`)  
   Calculates piping, macro-stability, overtopping, and combined dike-failure probabilities.

3. **Inundation** (`modules/inundation/`)  
   Uses breach discharge to calculate flooding depths for the affected compartments.

4. **Damage** (`modules/damage/`)  
   Converts inundation depths into total damage and casualties.
   
5. **Risk** (`modules/risk/`)  
   Combines flood probability and consequences into risk damage and risk casualties.

## Installation

Install the required Python packages with:

```bash
pip install -r requirements.txt
```
