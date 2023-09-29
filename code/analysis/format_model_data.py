import pandas as pd
import os

DATA_PATH = "../../data/results"

harm_ratings = pd.read_csv("../../data/ratings/average_harm.csv", delimiter=';')
harm_ratings.columns = ['means', 'side_effect']

good_ratings = pd.read_csv("../../data/ratings/average_good.csv", delimiter=';')
good_ratings.columns = ['means', 'side_effect']



def read_txt_to_int_list(file_path):
    with open(file_path) as f:
        return [int(line.strip()) for line in f.readlines()]

def expand_list(value, length):
    return [value] * length

full_df = {'model': [], 'method': [], 'causal_structure': [], 'evitability': [], 'action': [], 'permissibility_rating': [], 'intention_rating': [], 'scenario_id': []}

for cs, ev, ac, model, method in [(cs, ev, ac, model, method)
                                             for cs in ['means', 'side_effect']
                                             for ev in ['evitable', 'inevitable']
                                             for ac in ['action_yes', 'prevention_no']
                                             for model in ['claude-2', 'gpt-4-0613']
                                             for method in ['0shot', '0shot_cot']]:
    

    try:

        condition = f"{cs}_{ev}_{ac}"
        txt_file_permissibility = f"{model}_{method}_cot_kant_0.0_50_0_graded_answers_1.txt"
        txt_file_intention = f"{model}_{method}_cot_kant_0.0_50_0_graded_answers_2.txt"
        txt_file_path_permissibility = os.path.join(DATA_PATH, condition, txt_file_permissibility)
        txt_file_path_intention = os.path.join(DATA_PATH, condition, txt_file_intention)
        
        lines_permissibility = read_txt_to_int_list(txt_file_path_permissibility)
        lines_intention = read_txt_to_int_list(txt_file_path_intention)

        means = 0 if cs == 'side_effect' else 1
        evitable = 0 if ev == 'inevitable' else 1
        action = 0 if ac == 'prevention_no' else 1




        
        num_lines = len(lines_permissibility)
        full_df['model'].extend(expand_list(model, num_lines))
        full_df['method'].extend(expand_list(method, num_lines))
        full_df['causal_structure'].extend(expand_list(means, num_lines))
        full_df['evitability'].extend(expand_list(evitable, num_lines))
        full_df['action'].extend(expand_list(action, num_lines))
        full_df['permissibility_rating'].extend(lines_permissibility)
        full_df['intention_rating'].extend(lines_intention)
        full_df['scenario_id'].extend(list(range(0, num_lines)))

    except FileNotFoundError:
        print(f"Skipping {condition}")

df = pd.DataFrame(full_df)

# save to csv
df.to_csv(os.path.join(DATA_PATH, "model_results_long_kant_cot.csv"), index=False)