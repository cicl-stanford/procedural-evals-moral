import ast
import pandas as pd

DATA_PATH = "../../data/"
N_TRIALS = 16

df_trials = pd.read_csv(DATA_PATH + "prolific/trials.csv")
df_ids = pd.read_csv(DATA_PATH + "prolific/pid.csv")
df_exit = pd.read_csv(DATA_PATH + "prolific/exit_survey.csv")
# Read the CSV with a semicolon as the delimiter
harm_ratings = pd.read_csv(DATA_PATH + "ratings/harm.csv", delimiter=';', header=None)
harm_ratings.columns = ['means', 'side_effect']


good_ratings = pd.read_csv(DATA_PATH + "ratings/good.csv", delimiter=';', header=None)
good_ratings.columns = ['evitable', 'inevitable']



# Initialize an empty list to hold the transformed data
data = []
a = True
# Loop over each row in the DataFrame
for i, row in df_trials.iterrows():

    prolific_id = df_ids.iloc[i]["prolificPid"]
    exit_survey = df_exit.iloc[i]
    age = exit_survey["age"]
    ethnicity = exit_survey["ethnicity"]
    gender = exit_survey["gender"]
    race = exit_survey["race"]
    
    # Loop over trials
    for trial in range(1, N_TRIALS + 1):
        # Get item ratings
        item = ast.literal_eval(row[f"trial{trial}"])
        item_ratings = item["likertResponses"]
        ratings = [int(item_ratings[key]) for key in sorted(item_ratings.keys())]


        condition = item["condition"]

        if 'means' in condition:
            causal_structure = 1
            harm = list(harm_ratings['means'])[int(item['scenario_id'])]
            good = list(good_ratings['evitable'])[int(item['scenario_id'])]

        if 'side_effect' in condition:
            causal_structure = 0
            harm = list(harm_ratings['side_effect'])[int(item['scenario_id'])]
            good = list(good_ratings['inevitable'])[int(item['scenario_id'])]

        if 'evitable' in condition:
            evitability = 1

        if 'inevitable' in condition:
            evitability = 0

        if 'action_yes' in condition:
            action = 1

        if 'prevention_no' in condition:
            action = 0
      
        # Append transformed data to the list
        data.append({
            "split": row["proliferate.condition"],
            "worker_id": row["workerid"],
            # "prolific_id": prolific_id,
            # "age": age,
            # "ethnicity": ethnicity,
            # "gender": gender,
            # "race": race, 
            # "causal_structure_sentence": item["background"],
            # "condition": item["condition"],
            "scenario_id": item["scenario_id"],
            "scenario_harm": 0,
            "harm": harm,
            "good": good,
            # "evitability_sentence": item["evitability"],
            # "action_sentence": item["action"],
            "permissibility_rating": ratings[0],
            "intention_rating": ratings[1],
            "causal_structure": causal_structure,
            "evitability": evitability,
            "action": action,
            "full_scenario": item["background"] + " " + item["evitability"] + " " + item["action"]
        })


# Convert the list of dictionaries into a DataFrame
df_long = pd.DataFrame(data)

# Save the DataFrame as a CSV file
df_long.to_csv(DATA_PATH + "data_long.csv", index=False)