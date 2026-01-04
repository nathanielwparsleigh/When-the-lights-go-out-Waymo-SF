from utils import read_blackout_window

blackout_start, blackout_end = read_blackout_window(
    "data/blackout_window_251220SF.csv"
)

print("Blackout starts at:", blackout_start)
print("Blackout ends at  :", blackout_end)
print("Duration (hours):", (blackout_end - blackout_start).total_seconds() / 3600)
