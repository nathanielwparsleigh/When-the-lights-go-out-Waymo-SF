import os
import matplotlib.pyplot as plt

"""
run_experiment.py

This script runs the main experiment for Passion Project 1:

"When the Lights Go Out:
 The cost of delayed blackout detection in autonomous EV fleets"
"""

from datetime import timedelta
import numpy as np

from utils import read_blackout_window
from fleet_env import FleetEnv, FleetParams
from controllers import charge_lowest_soc_first


# -----------------------------
# Experiment configuration
# -----------------------------

TIME_STEP_MINUTES = 15
DETECTION_DELAYS_MINUTES = [0, 15, 30, 60]
BLACKOUT_CSV_PATH = "data/blackout_window_251220SF.csv"


# -----------------------------
# Helper: check blackout status
# -----------------------------

def is_blackout_active(current_time, blackout_start, blackout_end):
    """
    Returns True if the grid is actually down at current_time.
    """
    return blackout_start <= current_time < blackout_end


# -----------------------------
# Core experiment
# -----------------------------

def run_single_delay_experiment(detection_delay_minutes):
    """
    Run the fleet simulation for ONE blackout detection delay.
    """

    delay_steps = detection_delay_minutes // TIME_STEP_MINUTES

    blackout_start, blackout_end = read_blackout_window(BLACKOUT_CSV_PATH)

    sim_start_time = blackout_start - timedelta(hours=2)
    sim_end_time = blackout_end + timedelta(hours=2)

    params = FleetParams()
    env = FleetEnv(params=params, seed=0)

    perceived_blackout_start_step = None
    max_stranded = 0

    current_time = sim_start_time
    step = 0

    while current_time <= sim_end_time:

        blackout_now = is_blackout_active(current_time, blackout_start, blackout_end)

        if blackout_now and perceived_blackout_start_step is None:
            perceived_blackout_start_step = step + delay_steps

        blackout_detected = (
            perceived_blackout_start_step is not None
            and step >= perceived_blackout_start_step
        )

        grid_available = not blackout_now or not blackout_detected

        vehicles_to_charge = charge_lowest_soc_first(
            env.soc,
            params.max_vehicles_charging_at_once,
        )

        info = env.step(
            vehicles_to_charge=vehicles_to_charge,
            grid_available=grid_available,
        )

        max_stranded = max(max_stranded, info["stranded"])

        current_time += timedelta(minutes=TIME_STEP_MINUTES)
        step += 1

    return {
        "delay_minutes": detection_delay_minutes,
        "max_stranded": max_stranded,
        "failed_charging_attempts": env.failed_charging_attempts,
    }


# -----------------------------
# Plotting
# -----------------------------

def save_delay_plot(results, output_path):
    """
    Save the main figure:
    detection delay vs stranded vehicles
    """
    delays = [r["delay_minutes"] for r in results]
    stranded = [r["max_stranded"] for r in results]

    plt.figure()
    plt.plot(delays, stranded, marker="o")
    plt.title("When the Lights Go Out: Delay vs Stranded Vehicles")
    plt.xlabel("Blackout detection delay (minutes)")
    plt.ylabel("Max stranded vehicles (count)")
    plt.xticks(delays)
    plt.tight_layout()

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path, dpi=200)
    plt.close()

    print(f"\nSaved plot to: {output_path}")

def save_failed_charging_plot(results, output_path):
    """
    Save a plot:
      x = detection delay (minutes)
      y = failed charging attempts

    This shows how much the system keeps "trying to do the wrong thing"
    when it has not yet detected the blackout.
    """
    delays = [r["delay_minutes"] for r in results]
    failed = [r["failed_charging_attempts"] for r in results]

    plt.figure()
    plt.plot(delays, failed, marker="o")
    plt.title("Hidden damage: Failed charging attempts vs detection delay")
    plt.xlabel("Blackout detection delay (minutes)")
    plt.ylabel("Failed charging attempts (count)")
    plt.xticks(delays)
    plt.tight_layout()

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path, dpi=200)
    plt.close()

    print(f"Saved plot to: {output_path}")

# -----------------------------
# Main entry point
# -----------------------------

def main():
    print("\nRunning blackout detection delay experiment\n")

    results = []

    for delay in DETECTION_DELAYS_MINUTES:
        print(f"Running delay = {delay} minutes...")
        res = run_single_delay_experiment(delay)
        results.append(res)

    print("\nSummary results:")
    for r in results:
        print(
            f"Delay {r['delay_minutes']:>2} min | "
            f"Max stranded vehicles: {r['max_stranded']:>3} | "
            f"Failed charging attempts: {r['failed_charging_attempts']:>4}"
        )

    # Plot INSIDE main 
    save_delay_plot(results, "results/figures/delay_vs_stranded.png")
    save_failed_charging_plot(results, "results/figures/delay_vs_failed_charging.png")


if __name__ == "__main__":
    main()
