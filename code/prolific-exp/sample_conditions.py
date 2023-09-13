import random
import os
import json

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
            
# variables
causal_structure = ['means', 'side_effect']
evitability = ['evitable', 'inevitable']
action = ['action_yes', 'prevention_no']

# Random scenarios
random_scenario_idx = random.sample(range(0, NUM_STORIES), NUM_SCENARIOS)
random_scenario_idx = [39, 18, 24, 34, 31, 23, 10, 2, 19, 4] # sampled 09-12-2023 6:31pm

# Full data dict
data = {}

# Loop through all variables to generate condition names
for cs in causal_structure:
    for ev in evitability:
        for act in action:
            # Concatenate to form the condition name
            condition_name = f"{cs}_{ev}_{act}"
            
            # Construct the path to the CSV file for this condition
            csv_path = os.path.join(DATA_DIR, condition_name, 'stories.csv')
            
            # Assuming csv_path is valid and the file exists, read the CSV file
            try:
                csv_data = read_csv(csv_path)
            except FileNotFoundError:
                print(f"File {csv_path} not found.")
                continue
            
            # Selectt rows based on random scenario indices
            data[condition_name] = [csv_data[i] for i in random_scenario_idx]

# Initialize an empty list to keep track of used indices for each key
used_indices = {key: [] for key in data.keys()}

for batch in range(N_BATCH):
    stories = []  # Create an empty list to collect stories for this batch
    
    for key in data.keys():
        available_indices = [i for i in range(len(data[key])) if i not in used_indices[key]]
        
        # Randomly sample two different entries for this key
        sample_indices = random.sample(available_indices, 2)
        
        # Add these indices to used_indices to ensure they won't be used again
        used_indices[key].extend(sample_indices)
        
        for idx in sample_indices:
            background = data[key][idx][0] + ' ' + data[key][idx][1]
            evitability = data[key][idx][2]
            action = data[key][idx][3]
            
            # Create the story and add it to the list for this batch
            story = {'background': background, 'evitability': evitability, 'action': action}
            stories.append(story)
    
    # Write the stories list to a JSON file
    with open(f'batch_{batch}.json', 'w') as f:
        json.dump(stories, f)