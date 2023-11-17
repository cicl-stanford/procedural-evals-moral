import random
import csv
import tqdm
import argparse
import ast
import os
import json

from langchain.schema import (
    AIMessage,
    HumanMessage,
    SystemMessage
)

from utils import push_data, get_num_items, get_vars_from_out, get_llm

letters = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L',
           'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W','X', 'Y', 'Z']
DATA_DIR = '../../data'
PROMPT_DIR = '../prompt_instructions'
CSV_NAME = 'morality_stage_1_new'
SEVERITY_LEVELS = ['Mild', 'Extreme']

# Map story items to tags
STORY_TAGS = json.load(open('story_tags.json'))


parser = argparse.ArgumentParser()
parser.add_argument('--model', type=str, default='openai/gpt-4-0314', help='model name')
parser.add_argument('--temperature', type=float, default=0.5, help='temperature')
parser.add_argument('--max_tokens', type=int, default=2000, help='max tokens')
# change num completions to 10
parser.add_argument('--num_completions', type=int, default=1, help='number of completions')
parser.add_argument('--num_shots', type=int, default=3, help='number of shots')
parser.add_argument('--num_stories', type=int, default=2, help='number of stories to generate')
parser.add_argument('--verbose', type=bool, default=True, help='verbose')
parser.add_argument('--api', type=str, default='azure', help='which api to use')

def get_human_message(prompt_file):
    
    with(open(f'{PROMPT_DIR}/{prompt_file}.txt', 'r')) as f:
        msg = f.read().strip()
    letter_name, letter_profession = random.choice(letters), random.choice(letters)
    msg = msg.replace("[name_letter]", letter_name)
    msg = msg.replace("[profession_letter]", letter_profession)
    return msg


def gen_chat(args):
    response_template = "Here is the story:\n"
    for tag in STORY_TAGS:
        response_template += f"{tag}: {STORY_TAGS[tag]}\n"

    llm = get_llm(args)
    
    template_var = [tag.strip("{}") for tag in STORY_TAGS.values()]
    csv_file = f'{DATA_DIR}/{CSV_NAME}.csv'

    prompt_tokens_used = 0
    completion_tokens_used = 0

    # run loop with n stories, increase by num_completions
    for n_story in tqdm.tqdm(range(0, args.num_stories, args.num_completions)):
        # s = get_human_message('reminder_stage_1') # Why two text files?
        # new_message = s.split("Story (the")
        # human_message_1 = HumanMessage(content=new_message[0])
        instruction_text = get_human_message('morality_stage_1')
    

        system_message = SystemMessage(content=instruction_text)
        human_message_0 = HumanMessage(content='Generate a story')
    
        # Read examples from csv file every iteration to add generated samples to the pool of seed examples
        if args.verbose:
            print(f"Reading examples from {csv_file} with existing {get_num_items(csv_file)} examples")

        # Read a few examples from the csv file
        examples = []
        with open(csv_file, 'r') as f:
            for line in f.readlines():
                params = line.split(';')
                example = {k: params[v].strip() for v, k in enumerate(template_var)} 
                examples.append(example)
        random.shuffle(examples)

        # 2-shots by default	
        messages = [system_message]	
        for i in range(args.num_shots):	
            if i == len(examples):
                break
            messages.append(human_message_0)
            messages.append(AIMessage(content=response_template.format(**examples[i])))	
        # messages.append(human_message_1)	
        # if args.verbose:
        #     # print(f"------ messages ------")	
        #     # print(messages)	
        responses = llm.generate([messages], stop=["System:"])
        # prompt_tokens_used += responses.llm_output['token_usage']['prompt_tokens']
        # completion_tokens_used += responses.llm_output['token_usage']['completion_tokens']
        # price = (prompt_tokens_used * 0.03 + completion_tokens_used * 0.06) / 1000.
        # update tqdm progress bar with price
        # tqdm.tqdm.write(f"Price: {price:.2f} USD, Price per story: {price/(n_story+args.num_completions):.2f} USD")
        for g, generation in enumerate(responses.generations[0]):
            if args.verbose:
                print(f"------ Generated Story {n_story+g} ------")
                print(generation.text)
                # TODO - generate the table of story
                print("------------ Fin --------------")
     
            list_var = list(STORY_TAGS.keys())
            try:
                out_vars = get_vars_from_out(generation.text, list_var)
                # breakpoint()
            except:
                print("Error in parsing output")
                breakpoint()

            # Stitch together a story for each condition
            """
            +-------------+------------+--------------+---------------+--------------+
            |             | Mild harm, | Mild harm,   | Extreme harm, | Extreme harm,|
            |             | Mild good  | Extreme good | Mild good     | Extreme good |      
            +=============+============+==============+===============+===============+
            | Means,      |
            | Evitable,   |
            | Action      | 
            +-------------+
            | Means,      |
            | Inevitable, |
            | Action      |     
            +-------------+
            | Side Effect,|
            | Evitable,   |
            | Prevention  |      
            +-------------+
            | Side Effect,| 
            | Evitable,   | 
            | Action      | 
            +-------------+
            """
            
            all_conditions = ""
            for harm_type in SEVERITY_LEVELS:
                for good_type in SEVERITY_LEVELS:
                    # Run through 4 conditions

                    # (1) Means, Evitable, Action
                    all_conditions += f'----[Means, Evitable, Action] x [{harm_type} harm, {good_type} good]----\n'
                    all_conditions += " ".join([out_vars['Context'], out_vars['Situation CC'], 
                                    out_vars['Action CC'], out_vars[f'{harm_type} Harm CC'], 
                                    out_vars[f'{good_type} Good CC']]) + "\n\n"

                    # (2) Means, Inevitable, Action
                    all_conditions += f'----[Means, Inevitable, Action] x [{harm_type} harm, {good_type} good]----\n'
                    all_conditions += " ".join([out_vars['Context'], out_vars['Situation CC'], 
                                    out_vars['Action CC'], out_vars[f'{harm_type} Harm CC'], 
                                    out_vars[f'{good_type} Good CC'], out_vars['External Cause CC']]) + "\n\n"
                
                    # (3) Side Effect, Evitable, Prevention
                    all_conditions += f'----[Side Effect, Evitable, Prevention] x [{harm_type} harm, {good_type} good]----\n'
                    all_conditions += " ".join([out_vars['Context'], out_vars['Situation CoC'], 
                                    out_vars['Prevention CoC'], out_vars[f'{harm_type} Harm CoC'], 
                                    out_vars[f'{good_type} Good CoC']]) + "\n\n"
                
                    # (4) Side Effect, Evitable, Action
                    all_conditions += f'----[Side Effect, Evitable, Action] x [{harm_type} harm, {good_type} good]----\n'
                    all_conditions += " ".join([out_vars['Context'], out_vars['Situation CoC'], 
                                    out_vars['Action CoC'], out_vars[f'{harm_type} Harm CoC'], 
                                    out_vars[f'{good_type} Good CoC']]) + "\n\n"

            data = [out_vars[k] for k in list_var]
            
            # TODO - remove this later
            with open(f'{DATA_DIR}/temp_stories.txt', 'a') as file:
                file.write(all_conditions)

            story_file = f'{DATA_DIR}/{CSV_NAME}.csv'
            with open(f'{DATA_DIR}/effects.csv', 'a') as file:
                file.write(f'{out_vars["Mild Good CC"]},{out_vars["Extreme Good CC"]},{out_vars["Mild Harm CC"]},{out_vars["Extreme Harm CC"]},{out_vars["Mild Good CoC"]},{out_vars["Extreme Good CoC"]}{out_vars["Mild Harm CoC"]},{out_vars["Extreme Harm CoC"]}\n')

            with open(story_file, 'a') as csvfile:
                writer = csv.writer(csvfile, delimiter=';')
                writer.writerow(data)
        # push to github
        # push_data(DATA_DIR, REPO_URL)
    
    
if __name__ == "__main__":
    args = parser.parse_args()
    # print(f"Generating {args.num_stories} stories")
    # if args.verbose:
    #     print(args)
    gen_chat(args)
