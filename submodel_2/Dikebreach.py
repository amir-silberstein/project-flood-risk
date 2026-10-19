# -*- coding: utf-8 -*-
"""
Created on Fri Oct 16 14:05:32 2026

@author: vaida
"""

# -*- coding: utf-8 -*-
"""
Created on Sat Oct 10 13:59:09 2026

@author: vaida
"""

import contextlib
import io
import math
import pandas as pd

DT = 10  # seconds
B0 = 20  # meters
TD = 600  # seconds
G = 10  # m/s^2
UC = 0.2  # m/s
F1 = 1.2
F2 = 0.04
R = 2 / 3
BREACH_DURATION = 72 * 3600  # seconds
M = 1  # discharge coefficient

def simulate_breach(water_level_NAP, crest_height, floodplains_bed, t_end=BREACH_DURATION, dt=DT,B_initial=B0,):
  B = B_initial
  n_steps = int(t_end / dt) + 1
  MAX_DBDT = 1.0
  target_discharge = None

  for i in range(n_steps):
    t = i * dt
    if t <= TD:
      z_t = crest_height - (crest_height - floodplains_bed) * (t / TD)
      dBdt = 0.0
    else:
      z_t = floodplains_bed
      h_up = max(0.0, water_level_NAP - z_t)
      if h_up > 0:
        h_down = R * h_up
        head_difference = h_up - h_down
        if head_difference > 0:
          t_horiz = t - TD
          numerator = F1 * F2 * ((G * head_difference) ** 1.5)
          denominator = math.log(10) * (UC ** 2) * (1 + (F2 * G / UC) * t_horiz)
          dBdt = min(numerator / denominator, MAX_DBDT)
        else:
          dBdt = 0.0
      else:
        dBdt = 0.0

    if B >= 100.0:
      B = 100.0
      dBdt = 0.0

    h_up = max(0.0, water_level_NAP - z_t)
    Q_breach = (
        (2 / 3) ** 1.5 * (G ** 0.5) * B * (h_up ** 1.5) * M if h_up > 0 else 0.0
    )

    if B >= 100.0 and target_discharge is None:
      target_discharge = Q_breach

    B += dBdt * dt

  return target_discharge if target_discharge is not None else Q_breach


def run_analysis(dike_module_name):
  dike_mod = __import__(
      dike_module_name,
      fromlist=["water_level_data", "CrestHeightNAP", "FloodplainsBedNAP"],
  )
  water_level_data = dike_mod.water_level_data
  crest_height = dike_mod.CrestHeightNAP
  floodplains_bed = dike_mod.FloodplainsBedNAP

  with contextlib.redirect_stdout(io.StringIO()):
    return_periods, discharges, water_levels, _, _, _ = water_level_data()

  data = []
  for T, Q, wl in zip(return_periods, discharges, water_levels):
    overtopping = wl > crest_height
    breach_q = simulate_breach(wl, crest_height, floodplains_bed)
    status = "WARNING: Overtopping" if overtopping else ""

    data.append({
        "Return period": f"{T} years",
        "Discharge Lobith": f"{Q} m3/s",
        "Water level (NAP)": f"{wl:.2f} m",
        "Breach Discharge (B=100m)": f"{breach_q:.2f} m3/s",
        "Status": status,
    })

  df = pd.DataFrame(data)

  print(f"\n--- {dike_module_name} ---")
  header = "Return period | Discharge Lobith | Water level (NAP) | Breach Discharge (B=100m)"
  print(header)
  print("-" * len(header))

  for _, row in df.iterrows():
    line = f"{row['Return period']:<13} | {row['Discharge Lobith']:<16} | {row['Water level (NAP)']:<17} | {row['Breach Discharge (B=100m)']}"
    if row["Status"]:
      line += f" | {row['Status']}"
    print(line)


if __name__ == "__main__":
  for dike in ["Dike16_NAP", "Dike43_NAP"]:
    run_analysis(dike)