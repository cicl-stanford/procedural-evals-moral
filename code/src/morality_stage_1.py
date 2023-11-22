import random
import csv
import tqdm
import os
import argparse
import ast
import os
import json
import uuid 

#from langchain.chat_models import ChatOpenAI, AzureChatOpenAI
from langchain.schema import (
    AIMessage,
    HumanMessage,
    SystemMessage
)

# from crfm import crfmChatLLM

from utils import push_data, get_num_items, get_vars_from_out, get_llm

letters = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L',
           'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W','X', 'Y', 'Z']
DATA_DIR = '../../data'
PROMPT_DIR = '../prompt_instructions'
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
    msg = msg.replace("[profession_letter]", f"\'{letter_profession.lower()}\'")
    return msg

def gen_chat(args):
    response_template = "Here is the story:\n"
    for tag in STORY_TAGS:
        response_template += f"{tag}: {STORY_TAGS[tag]}\n"

    llm = get_llm(args)
    
    template_var = [tag.strip("{}") for tag in STORY_TAGS.values()]
    story_file = f'{DATA_DIR}/morality_stage_1_new.csv'

    prompt_tokens_used = 0
    completion_tokens_used = 0

    # Run loop with n stories, increase by num_completions
    for n_story in tqdm.tqdm(range(0, args.num_stories, args.num_completions)):
        instruction_text = get_human_message('morality_stage_1')

        system_message = SystemMessage(content=instruction_text)
        human_message= HumanMessage(content='Generate a story')
    
        # Read examples from csv file every iteration to add generated samples to the pool of seed examples
        if args.verbose:
            print(f"Reading examples from {story_file} with {get_num_items(story_file)} existing examples")

        # Read a few examples from the csv file
        examples = []
        with open(story_file, 'r') as f:
            for line in f.readlines():
                if ';' not in line:
                    continue
                params = line.split(';')
                example = {k: params[v].strip() for v, k in enumerate(template_var)} 
                examples.append(example)
        random.shuffle(examples)

        # 2-shots by default	
        messages = [system_message]	
        for i in range(args.num_shots):	
            if i == len(examples):
                break
            messages.append(human_message)
            messages.append(AIMessage(content=response_template.format(**examples[i])))	
  
        responses = llm.generate([messages], stop=["System:"])
       
        for g, generation in enumerate(responses.generations[0]):
            if args.verbose:
                print(f"------ Generated Story {n_story+g} ------")
                print(generation.text)
                print("------------ Fin --------------")
     
            out_vars = get_vars_from_out(generation.text)
           
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
            # Give unique story ID to cross-reference later
            story_id = uuid.uuid1().hex
            conditions = [story_id]
            for harm_type in SEVERITY_LEVELS:
                for good_type in SEVERITY_LEVELS:
                    # (1) Means, Evitable, Action
                    condition = " ".join([out_vars['Context'], out_vars['Situation CC'], out_vars['Evitable Action CC']]) 
                    conditions.append(condition)

                    # (2) Means, Inevitable, Action
                    condition = " ".join([out_vars['Context'], out_vars['Situation CC'], out_vars['Inevitable Action CC']])
                    conditions.append(condition)

                    # (3) Side Effect, Evitable, Prevention
                    condition = " ".join([out_vars['Context'], out_vars['Situation CoC'], out_vars['Evitable Prevention CoC']]) 
                    conditions.append(condition)

                    # (4) Side Effect, Evitable, Action
                    condition = " ".join([out_vars['Context'], out_vars['Situation CoC'], out_vars['Evitable Action CoC']]) 
                    conditions.append(condition)

            
            data = [out_vars[k] for k in STORY_TAGS]
            data.insert(0, story_id) 

            # Separate story components by tag
            with open(story_file, 'a') as csvfile:
                writer = csv.writer(csvfile, delimiter=';')
                writer.writerow(data)

            # For 4x4 table 
            with open(f'{DATA_DIR}/all_conditions.csv', 'a') as csvfile:
                writer = csv.writer(csvfile, delimiter=';')
                writer.writerow(conditions)


        # push to github
        # push_data(DATA_DIR, REPO_URL)
    
    
if __name__ == "__main__":
    args = parser.parse_args()
    gen_chat(args)
