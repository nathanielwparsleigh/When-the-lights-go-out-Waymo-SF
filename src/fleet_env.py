"""
fleet_env.py

This file defines our simple simulation world:

- We have a fleet of electric vehicles.
- Each vehicle has a battery level called State of Charge (SoC).
  (State of Charge is a fraction from 0.0 to 1.0)
- Every time step, vehicles "use energy" (they drive around).
- The depot can recharge some vehicles each step (like plugging them in).

Later we will add: blackouts + detection delays.
For now we only build the world.
"""

from dataclasses import dataclass
import numpy as np


@dataclass
class FleetParams:
    """
    Parameters = knobs you can tweak.

    We keep them here so the rest of the code is readable.
    """
    n_vehicles: int = 50

    # Initial State of Charge range for vehicles (randomly assigned)
    soc_init_min: float = 0.30
    soc_init_max: float = 0.90

    # If State of Charge drops below this, we consider the vehicle "stranded"
    stranded_soc_threshold: float = 0.10

    # Energy consumption per step (how fast vehicles lose charge)
    # This is simplified; later you could make it more realistic.
    soc_consumption_per_step: float = 0.01

    # Depot charging constraint: how many vehicles can charge at once
    max_vehicles_charging_at_once: int = 10

    # How much State of Charge a vehicle gains per step if charging
    soc_charge_per_step: float = 0.03


class FleetEnv:
    """
    Fleet environment (simulator).
    """

    def __init__(self, params: FleetParams, seed: int = 0):
        self.params = params
        self.rng = np.random.default_rng(seed)

        # Each vehicle starts with a random State of Charge in [soc_init_min, soc_init_max]
        self.soc = self.rng.uniform(
            params.soc_init_min,
            params.soc_init_max,
            size=params.n_vehicles
        )

        # This will count how many charging requests failed (used later for blackouts)
        self.failed_charging_attempts = 0

        # Track time steps (0,1,2,3,...)
        self.t = 0

    def step(self, vehicles_to_charge: np.ndarray, grid_available: bool = True):
        """
        Advance simulation by 1 step.

        vehicles_to_charge:
          A boolean array of length n_vehicles.
          True means "try to charge this vehicle now".

        grid_available:
          If False, charging is impossible (blackout).

        Returns:
          A dictionary of info we can log/plot.
        """

        # 1) Vehicles consume energy (drive)
        self.soc -= self.params.soc_consumption_per_step

        # Battery can't go below 0
        self.soc = np.maximum(self.soc, 0.0)

        # 2) Charging
        if grid_available:
            # Get indices of vehicles requested for charging
            idx = np.where(vehicles_to_charge)[0]

            # Enforce depot charging capacity
            if len(idx) > self.params.max_vehicles_charging_at_once:
                idx = idx[: self.params.max_vehicles_charging_at_once]

            # Charge those vehicles
            self.soc[idx] += self.params.soc_charge_per_step

            # Battery can't exceed 1
            self.soc = np.minimum(self.soc, 1.0)

        else:
            # Grid is down: any charging requests become "failed attempts"
            self.failed_charging_attempts += int(np.sum(vehicles_to_charge))

        # 3) Count stranded vehicles
        stranded = int(np.sum(self.soc < self.params.stranded_soc_threshold))

        # Advance time
        self.t += 1

        return {
            "t": self.t,
            "avg_soc": float(np.mean(self.soc)),
            "min_soc": float(np.min(self.soc)),
            "stranded": stranded,
            "failed_charging_attempts": self.failed_charging_attempts,
        }
