"""
controllers.py

This file defines simple "brains" that decide which vehicles to charge.

Important:
- These are intentionally simple rules.
- The point of the project is not fancy AI.
- The point is to study what happens when the system notices a blackout late.

We will implement two behaviors later:
1) Blackout-oblivious: keeps charging like normal (doesn't realize power is gone)
2) Blackout-aware: stops charging once it knows about the blackout

For now, both controllers will use the same basic "common sense" charging rule:
  "charge the vehicles with the lowest State of Charge first"
"""

import numpy as np


def charge_lowest_soc_first(soc_array, max_to_charge):
    """
    Simple rule:
    - Find vehicles with lowest battery (State of Charge).
    - Try to charge up to max_to_charge vehicles.

    Inputs:
      soc_array: numpy array of State of Charge values for each vehicle
      max_to_charge: integer, max vehicles allowed to charge this step

    Returns:
      vehicles_to_charge: boolean numpy array (True = charge this vehicle)
    """
    n = len(soc_array)

    # Get vehicle indices sorted by State of Charge (lowest first)
    order = np.argsort(soc_array)

    # Create a boolean mask: True for vehicles we want to charge
    vehicles_to_charge = np.zeros(n, dtype=bool)

    # Select the lowest-battery vehicles
    vehicles_to_charge[order[:max_to_charge]] = True

    return vehicles_to_charge
