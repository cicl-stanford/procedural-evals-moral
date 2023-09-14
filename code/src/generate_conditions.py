import os
import csv

DATA_DIR = '../../data'
CONDITION_DIR = os.path.join(DATA_DIR, 'conditions')
CSV_NAME = os.path.join(DATA_DIR, 'morality.csv')
INTENTION = ['means', 'side_effect']
ACTION = ['action_yes', 'prevention_yes', 'action_no', 'prevention_no']
EVITABILITY = ['evitable', 'inevitable']



def get_completions():
    with open(CSV_NAME, "r") as f:
        reader = csv.reader(f, delimiter=";")
        completions = list(reader)
    return completions

def generate_conditions(completions):
    list_var = ["Context", "Situation CC", "Harm CC", "Good CC", "Action CC", "Prevention CC", "External Cause CC", "CoC", "Good CoC", "Harm CoC", "Action CoC", "Prevention CoC", "External Cause CoC", "Evitable Action CC", "Inevitable Action CC", "Evitable Prevention CC", "Inevitable Prevention CC", "Action Sentence CC", "Prevention Sentence CC", "Evitable Action CoC", "Inevitable Action CoC", "Evitable Prevention CoC", "Inevitable Prevention CoC", "Action Sentence CoC", "Prevention Sentence CoC"]

    for completion_idx, completion in enumerate(completions):



        completion = completion[:-2]

        dict_var = {k:v for k,v in zip(list_var, completion)}
        context = dict_var['Context'] # context (constant)
        name = context.split(',')[0]
        belief_question = ""
        intention_question = ""
        belief_question = belief_question.format(name=name)
        intention_question = intention_question.format(name=name)

        for intention in INTENTION:

            if intention == 'means':
                situation = dict_var['Situation CC'] # CC
                harm = dict_var['Harm CC'] # Harm CC
                good = dict_var['Good CC'] # Good CC
               
                for evitabiltiy in EVITABILITY:
 
                    for action in ACTION:

                        if evitabiltiy == 'evitable':

                            if action == 'action_yes':
                                action_var = dict_var['Action CC']
                                evitable_action = dict_var['Evitable Action CC'] # Evitable Action CC
                                action_sentence = dict_var['Action Sentence CC'].split('.')[0] + "."
                            
                            if action == 'action_no':
                                action_var = dict_var['Action CC']
                                evitable_action = dict_var['Evitable Action CC']
                                action_sentence =dict_var['Action Sentence CC'].split('.')[1][1:] + "."
              
                            
                            if action == 'prevention_yes':
                                action_var = dict_var['Prevention CC']
                                evitable_action = dict_var['Evitable Prevention CC']
                                action_sentence = dict_var['Prevention Sentence CC'].split('.')[0] + "."
                            
                            if action == 'prevention_no':
                                action_var = dict_var['Prevention CC']
                                evitable_action = dict_var['Evitable Prevention CC']
                                action_sentence = dict_var['Prevention Sentence CC'].split('.')[1][1:] + "."
                
                        if evitabiltiy == 'inevitable':

                            if action == 'action_yes':
                                action_var = dict_var['Action CC']
                                evitable_action = dict_var['Inevitable Action CC']
                                action_sentence = dict_var['Action Sentence CC'].split('.')[0] + "."
                            
                            if action == 'action_no':
                                action_var = dict_var['Action CC']
                                evitable_action = dict_var['Inevitable Action CC']
                                action_sentence = dict_var['Action Sentence CC'].split('.')[1][1:]
                            
                            if action == 'prevention_yes':
                                action_var = dict_var['Prevention CC']
                                evitable_action = dict_var['Inevitable Prevention CC']
                                action_sentence = dict_var['Prevention Sentence CC'].split('.')[0] + "."
                            
                            if action == 'prevention_no':
                                action_var = dict_var['Prevention CC']
                                evitable_action = dict_var['Inevitable Prevention CC']
                                action_sentence = dict_var['Prevention Sentence CC'].split('.')[1][1:] + "."


                        # Check if the new file needs to be created or appended
                        if not os.path.exists(os.path.join(CONDITION_DIR, f'{intention}_{evitabiltiy}_{action}')):
                            os.makedirs(os.path.join(CONDITION_DIR, f'{intention}_{evitabiltiy}_{action}'))
                        new_csv_file = os.path.join(CONDITION_DIR, f'{intention}_{evitabiltiy}_{action}', f'stories.csv')
                        with open(new_csv_file, "a" if completion_idx > 0 else "w", newline='') as csvfile:
                            writer = csv.writer(csvfile, delimiter=";")
                            writer.writerow([context, situation, f"Harm (Necessary): {harm}", f"Good: {good}", evitable_action, action_sentence, belief_question, intention_question])


            if intention == 'side_effect':

                situation = dict_var['CoC'] # CoC
                harm = dict_var['Harm CoC'] # Harm CoC
                good = dict_var['Good CoC'] # Good CoC

                for evitabiltiy in EVITABILITY:

                    for action in ACTION:

                        if evitabiltiy == 'evitable':

                            if action == 'action_yes':
                                action_var = dict_var['Action CoC']
                                evitable_action = dict_var['Evitable Action CoC']
                                action_sentence = dict_var['Action Sentence CoC'].split('.')[0]

                            if action == 'action_no':
                                action_var = dict_var['Action CoC']
                                evitable_action = dict_var['Evitable Action CoC']
                                action_sentence = dict_var['Action Sentence CoC'].split('.')[1][1:]
                            if action == 'prevention_yes':
                                action_var = dict_var['Prevention CoC']
                                evitable_action = dict_var['Evitable Prevention CoC']
                                action_sentence = dict_var['Prevention Sentence CoC'].split('.')[0]
                            if action == 'prevention_no':
                                action_var = dict_var['Prevention CoC']
                                evitable_action = dict_var['Evitable Prevention CoC']
                                action_sentence = dict_var['Prevention Sentence CoC'].split('.')[1][1:]
                    
                        if evitabiltiy == 'inevitable':

                       
                            if action == 'action_yes':
                                action_var = dict_var['Action CoC']
                                evitable_action = dict_var['Inevitable Action CoC']
                                action_sentence = dict_var['Action Sentence CoC'].split('.')[0]
                            if action == 'action_no':
                                action_var = dict_var['Action CoC']
                                evitable_action = dict_var['Inevitable Action CoC']
                                action_sentence = dict_var['Action Sentence CoC'].split('.')[1][1:]
                            if action == 'prevention_yes':
                                action_var = dict_var['Prevention CoC']
                                evitable_action = dict_var['Inevitable Prevention CoC']
                                action_sentence = dict_var['Prevention Sentence CoC'].split('.')[0]
                            if action == 'prevention_no':
                                action_var = dict_var['Prevention CoC']
                                evitable_action = dict_var['Inevitable Prevention CoC']
                                action_sentence = dict_var['Prevention Sentence CoC'].split('.')[1][1:]

                        
                        # Check if the new file needs to be created or appended
                        if not os.path.exists(os.path.join(CONDITION_DIR, f'{intention}_{evitabiltiy}_{action}')):
                            os.makedirs(os.path.join(CONDITION_DIR, f'{intention}_{evitabiltiy}_{action}'))
                        new_csv_file = os.path.join(CONDITION_DIR, f'{intention}_{evitabiltiy}_{action}', f'stories.csv')
                        with open(new_csv_file, "a" if completion_idx > 0 else "w", newline='') as csvfile:
                            writer = csv.writer(csvfile, delimiter=";")
                            writer.writerow([context, situation, f"Good: {good}", f"Harm (Side Effect): {harm}", evitable_action, action_sentence, belief_question, intention_question])



if __name__ == "__main__":  
    completions = get_completions()
    generate_conditions(completions)
