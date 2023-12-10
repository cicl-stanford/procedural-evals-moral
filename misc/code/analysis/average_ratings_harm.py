import os
import pandas as pd
from collections import defaultdict

DATA_PATH = "../../data/ratings"
RATINGS = ["harm", "good"]
NAMES = ["priya", "eric", "david", "ben", "sying"]

# Initialize a dictionary to hold DataFrames of each rating type
rating_dfs = defaultdict(list)

# Loop over ratings and names
for rating in RATINGS:
    for name in NAMES:
        path = os.path.join(DATA_PATH, f"{rating}_{name}.csv")
        
        # Check if the file exists
        if not os.path.exists(path):
            print(f"File {path} does not exist. Skipping...")
            continue

        # Load the DataFrame and append it to the respective rating type list in the dictionary
        df = pd.read_csv(path, delimiter=';', header=None, names=['means', 'side_effect'])
        rating_dfs[rating].append(df)

# Calculate the element-wise mean for each rating type and save the averaged DataFrame
averaged_frames = {}  # This dictionary will hold the averaged DataFrames, one for 'harm' and one for 'good'

for rating, dfs in rating_dfs.items():
    if dfs:
        avg_df = pd.concat(dfs).groupby(level=0).mean().round(3)  # Calculate the element-wise mean and round it to 2 decimal places
        averaged_frames[rating] = avg_df  # Store the averaged DataFrame in the dictionary
        
        # Save the averaged DataFrame to a CSV file
        avg_path = os.path.join(DATA_PATH, f"average_{rating}.csv")
        avg_df.to_csv(avg_path, sep=';', index=False)
        print(f"Averaged DataFrame saved at {avg_path}")