# SnF Script for Project 1

## How to Use
  - Make sure you have matplotlib, numPy, and imageio installed, and all associated files in the same directory.
  - Run main.py with desired settings in configs.json

## Configs
  - All parameters needed for the lab are in configs.json, such as the initial dimensions and fish. Configure the attempts parameter to set how many simulations run, 
  and set the values in the changesPerAttempt dictionary to set changes between runs.
  - For example, with attempts = 3 and d_initial_fish = 100, the simulation runs 3 times, incrementing the amount of intial fish in each run. First run starts with 2000, then 2100, then 2200. Treat the "d_" values as Δ.
    So, d_energy_gain is the Δ energy gain between each run, etc.


## Note
  -message me if anything breaks, send photo of error and configs file
