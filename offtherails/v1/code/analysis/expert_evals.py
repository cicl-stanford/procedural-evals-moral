import pandas as pd

DATA_PATH_EXPERT_1 = "../../data/ratings/ayesha.csv"
DATA_PATH_EXPERT_2 = "../../data/ratings/philipp.csv"

column_names = ["desired_format", "rating"]
desired_format_mapping = {'yes': 1, 'no': 0}

expert_1 = pd.read_csv(DATA_PATH_EXPERT_1, sep=";", skiprows=1, names=column_names)
expert_2 = pd.read_csv(DATA_PATH_EXPERT_2, sep=";", skiprows=1, names=column_names)

expert_1['rating'] = expert_1['rating'].astype(int)
expert_2['rating'] = expert_2['rating'].astype(int)

expert_1['desired_format'] = expert_1['desired_format'].map(desired_format_mapping)
expert_2['desired_format'] = expert_2['desired_format'].map(desired_format_mapping)

expert_1["item"] = expert_1.index
expert_2["item"] = expert_2.index

expert_1["expert"] = "expert_1"
expert_2["expert"] = "expert_2"

df = pd.concat([expert_1, expert_2], ignore_index=True)

df.to_csv("../../data/ratings/expert_combined.csv", index=False)

a = expert_1['desired_format'].to_list()
b = expert_2['desired_format'].to_list()

df = pd.DataFrame({"Rater 1": a, "Rater 2": b})

percentage_agreement = sum(df["Rater 1"] == df["Rater 2"]) / len(df) * 100

print(f"Percentage Agreement: {percentage_agreement}")
print(f"Average Ratings Rater 1: {expert_1['desired_format'].mean()}, {expert_1['rating'].mean()}")
print(f"""CI Ratings Rater 1: {expert_1['desired_format'].mean() + expert_1['desired_format'].sem() * 1.96}, {expert_1['desired_format'].mean() - expert_1['desired_format'].sem() * 1.96}, 
{expert_1['rating'].mean() + expert_1['rating'].sem() * 1.96}, {expert_1['rating'].mean() - expert_1['rating'].sem() * 1.96}""")
print(f"Average Ratings Rater 2: {expert_2['desired_format'].mean()}, {expert_2['rating'].mean()}")
print(f"""CI Ratings Rater 2: {expert_2['desired_format'].mean() + expert_2['desired_format'].sem() * 1.96}, {expert_2['desired_format'].mean() - expert_2['desired_format'].sem() * 1.96},
{expert_2['rating'].mean() + expert_2['rating'].sem() * 1.96}, {expert_2['rating'].mean() - expert_2['rating'].sem() * 1.96}""")