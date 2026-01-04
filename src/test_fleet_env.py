"""
A tiny test to prove FleetEnv works.

We charge the lowest-battery vehicles each step and print a few stats.
"""

import numpy as np
from fleet_env import FleetEnv, FleetParams


def main():
    params = FleetParams(n_vehicles=20, max_vehicles_charging_at_once=5)
    env = FleetEnv(params=params, seed=0)

    for step in range(10):
        # Strategy: charge the vehicles with the lowest battery first
        # (This is a simple "common sense" rule)
        order = np.argsort(env.soc)  # indices sorted from lowest SoC to highest
        vehicles_to_charge = np.zeros(params.n_vehicles, dtype=bool)
        vehicles_to_charge[order[: params.max_vehicles_charging_at_once]] = True

        info = env.step(vehicles_to_charge=vehicles_to_charge, grid_available=True)

        print(
            f"Step {step:02d} | avg State of Charge={info['avg_soc']:.3f} "
            f"| min={info['min_soc']:.3f} | stranded={info['stranded']}"
        )

    print("FleetEnv test complete ✅")


if __name__ == "__main__":
    main()
