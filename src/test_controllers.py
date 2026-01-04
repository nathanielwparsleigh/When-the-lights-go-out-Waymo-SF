import numpy as np
from controllers import charge_lowest_soc_first

soc = np.array([0.9, 0.2, 0.5, 0.1, 0.7])
mask = charge_lowest_soc_first(soc, max_to_charge=2)

print("SoC values:", soc)
print("Charge mask:", mask)
print("Vehicles selected:", np.where(mask)[0])
