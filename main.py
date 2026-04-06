import json, sys, subprocess
from pathlib import Path


config_path = Path(__file__).parent / "configs.json"
try:
    with open(config_path, 'r') as file:
        data = json.load(file)
    print("File data =", data)
    
except json.JSONDecodeError:
    print("Error: Failed to decode JSON from the file.")


script_dir = Path(__file__).parent
command = [sys.executable, "test.py", "3"]

subprocess.run(command, cwd=script_dir)

