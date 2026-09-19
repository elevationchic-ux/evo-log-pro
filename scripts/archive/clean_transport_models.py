import os, sys

sys.stdout.reconfigure(encoding='utf-8')

path = 'ERP-logistique-/evo-log-backend/app/models/transport_avance.py'
with open(path, 'r', encoding='utf-8', errors='ignore') as f:
    lines = f.readlines()

# Part 1: lines 0 to 513 (up to MaintenancePreventive)
part1 = lines[:513]

# Extract PositionGPS definition (from line 754 to line 782)
part_gps = lines[753:782]

# Extract ZoneGeofencing and EvenementVehicule (from line 1023 to line 1064)
part_geo = lines[1023:1064]

new_lines = part1 + part_gps + part_geo

with open(path, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print(f"Cleaned {path}: reduced from {len(lines)} to {len(new_lines)} lines.")
