import os
from skyfield.api import Loader, load

# Set a path for the data files
data_path = '/home/ubuntu/skyfield-data'
if not os.path.exists(data_path):
    os.makedirs(data_path)

# Create a loader that uses that path
load = Loader(data_path)

# Try to load the ephemeris file with explicit download
try:
    eph = load('de440.bsp')
    print("Successfully loaded de440.bsp")
except Exception as e:
    print(f"Error loading de440.bsp: {e}")

ts = load.timescale()
print("Successfully loaded timescale")

# Set t_in from the CSL file
t_in = ts.from_iso("2025-10-18T00:00:00Z")
print(f"t_in: {t_in}")
