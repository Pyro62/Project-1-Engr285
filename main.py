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
    for i in range(run["attempts"]):
        changes = run["changesPerAttempt"][0]
        command = [sys.executable, "SnF.py",
                    str(run["breed_time"]+(i*changes["d_breed_time"])),
                    str(run["energy_gain"]+(i*changes["d_energy_gain"])),
                    str(run["breed_energy"]+(i*changes["d_breed_energy"])),
                    str(run["dims_x"]+(i*changes["d_dims_x"])),
                    str(run["dims_y"]+(i*changes["d_dims_y"])),
                    str(run["initial_fish"]+(i*changes["d_initial_fish"])),
                    str(run["initial_sharks"]+(i*changes["d_initial_sharks"])),
                    str(run["steps"]+(i*changes["d_steps"])),
                    str(run["basicSetup"]),
                    str(i)]
        subprocess.run(command, cwd=script_dir)





