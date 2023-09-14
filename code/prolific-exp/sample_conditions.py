from collections import defaultdict
import json
import os
import numpy as np

# Constants
DATA_DIR = '../../data/conditions'
NUM_CONDITIONS = 8
NUM_SCENARIOS = 10
NUM_BATCHES = 10

# Function to read CSV
def read_csv(csv_file):
    with open(csv_file, 'r') as f:
        lines = f.readlines()
    for i, line in enumerate(lines):
        lines[i] = line.strip().split(';')
    return lines

# Define all conditions
causal_structure = ['means', 'side_effect']
evitability = ['evitable', 'inevitable']
action = ['action_yes', 'prevention_no']

# Sample 10 random indexes between 0 and 50 without replacement 
rand_story_idxs = np.random.choice(50, NUM_SCENARIOS, replace=False) # [24  1  4 46 13 47 22 16  0 33]
print(rand_story_idxs)

# Initialize batches
batches = [[] for _ in range(NUM_BATCHES)]

# Generate all stories
for batch_idx in range(NUM_BATCHES):
    random_idx = rand_story_idxs[batch_idx]
    for cs in causal_structure:
        for ev in evitability:
            for act in action:
                condition_name = f"{cs}_{ev}_{act}"
                csv_path = os.path.join(DATA_DIR, condition_name, "stories.csv")
                try:
                    csv_data = read_csv(csv_path)
                except FileNotFoundError:
                    print(f"File {csv_path} not found.")
                    continue
                
                story_data = csv_data[random_idx]  # Get the story corresponding to the random index
                context, background, evitability_sentence, action_sentence = story_data
                story = {'background': context + " " + background, 'evitability': evitability_sentence, 'action': action_sentence, "condition": condition_name, "scenario_id": int(random_idx)}
                
                batches[batch_idx].append(story)

# Write the batches to JSON files
for i, batch in enumerate(batches):
    with open(f'batch_{i}.json', 'w') as f:
        json.dump(batch, f)
