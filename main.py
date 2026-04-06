import json, sys, subprocess
from pathlib import Path


config_path = Path(__file__).parent / "configs.json"
try:
    with open(config_path, 'r') as file:
        data = json.load(file)
    #print("File data =", data)
    
except json.JSONDecodeError:
    print("Error: Failed to decode JSON from the file.")

runs = data["runs"]
script_dir = Path(__file__).parent

for run in runs:
    command = [sys.executable, "SnF.py", str(run["breed_time"]),str(run["energy_gain"]),str(run["breed_energy"]),str(run["dims_x"]),
               str(run["dims_y"]),str(run["initial_fish"]),str(run["initial_sharks"]),str(run["steps"]),str(run["basicSetup"])]
    subprocess.run(command, cwd=script_dir)





