from collections import defaultdict
import json
import os
import numpy as np

# Constants
DATA_DIR = '../'
NUM_CONDITIONS = 8
NUM_SCENARIOS = 3
NUM_BATCHES = 1
PER_BATCH = NUM_CONDITIONS * NUM_SCENARIOS // NUM_BATCHES


# Function to read CSV
def read_csv(csv_file):
    with open(csv_file, 'r') as f:
        lines = f.readlines()
    for i, line in enumerate(lines):
        lines[i] = line.strip().split(';')
    return [l[:3] for l in lines]

# Define all conditions
causal_structure = ['cc', 'coc']

test_items = []

# Read all the data
for cs in causal_structure:
    csv_path = os.path.join(DATA_DIR, f"{cs}_stage_1_severe.csv")
    try:
        csv_data = read_csv(csv_path)
    except FileNotFoundError:
        print(f"File {csv_path} not found.")
        continue
    for s, story in enumerate(csv_data[:NUM_SCENARIOS]):
        if cs == 'cc':
            test_items.append({"text": story[0] + " " + story[1], "scenario_id": s, "structure": cs, "type": "harm", "strength": "severe"})
            test_items.append({"text": story[0] + " " + story[2], "scenario_id": s, "structure": cs, "type": "good", "strength": "severe"})
        elif cs == 'coc':
            test_items.append({"text": story[0] + " " + story[2], "scenario_id": s, "structure": cs, "type": "harm", "strength": "severe"})
            test_items.append({"text": story[0] + " " + story[1], "scenario_id": s, "structure": cs, "type": "good", "strength": "severe"})

with open(f'test_items_0.json', 'w') as f:
    json.dump(test_items, f)