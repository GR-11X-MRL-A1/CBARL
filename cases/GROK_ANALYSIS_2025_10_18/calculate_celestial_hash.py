'''
import json
import hashlib
import os
from skyfield.api import Loader
from datetime import datetime, timezone

# Set a path for the data files
data_path = '/home/ubuntu/skyfield-data'
if not os.path.exists(data_path):
    os.makedirs(data_path)

# Create a loader that uses that path
load = Loader(data_path)

# Load ephemeris data
ts = load.timescale()
eph = load('de440.bsp')

# Set t_in from the CSL file
dt = datetime.fromisoformat("2025-10-18T00:00:00+00:00")
t_in = ts.from_datetime(dt)

# Get positions of Sun and Jupiter
sun = eph['sun']
jupiter = eph['jupiter_barycenter']

# Calculate apparent positions from Earth
earth = eph['earth']
sun_pos = earth.at(t_in).observe(sun).apparent()
jupiter_pos = earth.at(t_in).observe(jupiter).apparent()

# Quantize the values (microrad for angles, microau for range)
lon_sun, lat_sun, dist_sun = sun_pos.ecliptic_latlon('J2000.0')
lon_jup, lat_jup, dist_jup = jupiter_pos.ecliptic_latlon('J2000.0')

quant_lon_sun = int(lon_sun.radians * 1e6)
quant_lat_sun = int(lat_sun.radians * 1e6)
quant_dist_sun = int(dist_sun.au * 1e6)

quant_lon_jup = int(lon_jup.radians * 1e6)
quant_lat_jup = int(lat_jup.radians * 1e6)
quant_dist_jup = int(dist_jup.au * 1e6)

# Pack as big-endian signed 64-bit integers
packed_data = b''
for val in [quant_lon_sun, quant_lat_sun, quant_dist_sun, quant_lon_jup, quant_lat_jup, quant_dist_jup]:
    packed_data += val.to_bytes(8, byteorder='big', signed=True)

# Hash the packed data
hash_object = hashlib.sha384(packed_data)
celestial_hash = hash_object.hexdigest()

print(celestial_hash)
'''
