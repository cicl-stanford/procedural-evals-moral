import random
import os
import json
from collections import Counter, defaultdict

NUM_CONDITIONS = 8
NUM_SCENARIOS = 10
NUM_STORIES = 50
N_BATCH = 5

DATA_DIR = '../../data/conditions/'

def read_csv(csv_file):
    with open(csv_file, 'r') as f:
        lines = f.readlines()
    for i, line in enumerate(lines):
        lines[i] = line.strip().split(';')
    return lines

# Variables
causal_structure = ['means', 'side_effect']
evitability = ['evitable', 'inevitable']
action = ['action_yes', 'prevention_no']

# Random scenarios
random_scenario_idx = random.sample(range(0, NUM_STORIES), NUM_SCENARIOS)

# Data dict
data = {}
for cs in causal_structure:
    for ev in evitability:
        for act in action:
            condition_name = f"{cs}_{ev}_{act}"
            csv_path = os.path.join(DATA_DIR, condition_name, 'stories.csv')
            try:
                csv_data = read_csv(csv_path)
            except FileNotFoundError:
                print(f"File {csv_path} not found.")
                continue
            data[condition_name] = [csv_data[i] for i in random_scenario_idx]

# Create a list of all stories
all_stories = []
for key in data.keys():
    for idx, story_data in enumerate(data[key]):
        background = story_data[0] + ' ' + story_data[1]
        evitability = story_data[2]
        action = story_data[3]
        story = {'background': background, 'evitability': evitability, 'action': action, "sample_idx": idx, "condition": key, "scenario_id": random_scenario_idx[idx]}
        all_stories.append(story)

# Shuffle the list of all stories
random.shuffle(all_stories)

# Initialize batches and scenario counter
batches = [[] for _ in range(N_BATCH)]
scenario_counter = Counter()

# Plan for each scenario: appear twice in 4 batches, and zero times in 1 batch
scenario_plan = defaultdict(lambda: [2, 2, 2, 2, 0])
for scenario_id in random_scenario_idx:
    random.shuffle(scenario_plan[scenario_id])

# Distribute stories into batches
for story in all_stories:
    for batch_idx in range(N_BATCH):
        # Check if this story's scenario should appear in this batch according to the plan
        if scenario_plan[story['scenario_id']][batch_idx] > 0:
            # Add the story to the batch
            batches[batch_idx].append(story)
            
            # Update the plan
            scenario_plan[story['scenario_id']][batch_idx] -= 1

# Write the batches to JSON files
for i, batch in enumerate(batches):
    with open(f'batch_{i}.json', 'w') as f:
        json.dump(batch, f)
