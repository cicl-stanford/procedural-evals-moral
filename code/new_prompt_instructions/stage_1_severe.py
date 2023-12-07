import random
import csv
import tqdm
import os
import argparse
import os
from typing import List

from langchain.schema import (
    AIMessage,
    HumanMessage,
    SystemMessage
)

from langchain.chat_models import AzureChatOpenAI

DATA_DIR = '../../data'
PROMPT_DIR = '../new_prompt_instructions'

def get_vars_from_out(out:str) -> List[str]:
    vars = []
    out = out.split('\n')
    out = [l for l in out if ':' in l]
    for line in out:
        elems = line.split(': ')
        vars.append(elems[1].strip())
    return vars


def get_llm(args):
    if args.api == 'azure':
        llm = AzureChatOpenAI(
            azure_endpoint="https://philipp.openai.azure.com/",
            openai_api_version="2023-05-15",
            deployment_name='gpt-4',
            openai_api_key=os.getenv("API_KEY"),
            openai_api_type="azure",
            temperature=args.temperature,
        )
    else:
        raise Exception(f"Unknown API {args.api}")
    return llm



CONDITION = ['CC', 'CoC']



def get_context(name, profession):
    # check if profession is noun
    if profession.strip()[0].lower() in ['a', 'e', 'i', 'o', 'u']:
        profession = f'an {profession.strip()}'
    else:
        profession = f'a {profession.strip()}'
    context = f"{name.strip()}, {profession}, faces a moral dilemma."
    return context

def get_example(names, professions, condition, rand_item):
    name = names[rand_item]
    profession = professions[rand_item]
    context = get_context(name, profession)
    
    vars = {k: None for k in range(17)}
    if condition == "CC":
        with open(f'{PROMPT_DIR}/cc_stage_1_severe.csv', 'r') as f:
            reader = csv.reader(f, delimiter=';')
            for i, row in enumerate(reader):
                if i == rand_item:
                    for j, elem in enumerate(row):
                        vars[j] = elem.strip()
                    break
        return f"""Context: {context}
Format
Action Opportunity: {vars[0]}
Necessary Severe Harm -> Very Good
Necessary Severe Harm: {vars[1]}
Very Good: {vars[2]}
Other Preventable Cause: {vars[3]}
External Non-Preventable Cause: {vars[4]}"""

    elif condition == "CoC":
        with open(f'{PROMPT_DIR}/coc_stage_1_severe.csv', 'r') as f:  
            reader = csv.reader(f, delimiter=';')
            for i, row in enumerate(reader):
                if i == rand_item:
                    for j, elem in enumerate(row):
                        vars[j] = elem.strip()
                    break
        return f"""Context: {context}
Format
Action Opportunity: {vars[0]}
Very Good with Severe Harm as a Side Effect
Very Good: {vars[1]}
Severe Harm: {vars[2]}
Other Preventable Cause: {vars[3]}
External Non-Preventable Cause: {vars[4]}"""
                

            
def gen_chat(args):
    llm = get_llm(args)

    # load names 
    with(open(f'{PROMPT_DIR}/names.txt', 'r')) as f:
        names = f.readlines()

    # load professions
    with(open(f'{PROMPT_DIR}/professions.txt', 'r')) as f: 
        professions = f.readlines()

   
    # loop over names 
    for i, name in enumerate(names[args.start:args.end]):
        # load profession
        profession = professions[i + args.start]
        # loop over conditions (CC, CoC)
        rand_item = 1 #random.randint(1) # random.randint(0, args.start - 1) # random example for few shot generation set to 1

        for condition in CONDITION:


            # messages sent to model 
            messages = []
            if condition == "CC":
                with(open(f'{PROMPT_DIR}/cc_stage_1_severe.txt', 'r')) as f:
                    system_prompt = f.read().strip()
            elif condition == "CoC":
                with(open(f'{PROMPT_DIR}/coc_stage_1_severe.txt', 'r')) as f:
                    system_prompt = f.read().strip()

            example = get_example(names, professions, condition, rand_item)

            system_message = SystemMessage(content=system_prompt)
            human_message_0 = HumanMessage(content=f"Generate a completion for this context: {get_context(name=names[rand_item], profession=professions[rand_item])}")
            ai_message_0 = AIMessage(content=example)
            human_message_1 = HumanMessage(content=f"""Generate a new completion for this context: {get_context(name=name, profession=profession)}
Reminder: You must follow this structure:
{system_prompt}""")
            messages.append(system_message)
            messages.append(human_message_0)
            messages.append(ai_message_0)
            messages.append(human_message_1)
            
            responses = llm.generate([messages], stop=["System:"])


            for g, generation in enumerate(responses.generations[0]):
                if args.verbose:
                    print(f"------ Generated Story ------")
                    print(generation.text)
                    print("------------ Fin --------------")

                
                vars = get_vars_from_out(generation.text)
                if len(vars) == 6:
                    vars = vars[1:]
    
                if condition == "CC":
                    with open(f'{PROMPT_DIR}/cc_stage_1_severe.csv', 'a') as csvfile:
                        writer = csv.writer(csvfile, delimiter=';')
                        writer.writerow(vars)
                elif condition == "CoC":
                    with open(f'{PROMPT_DIR}/coc_stage_1_severe.csv', 'a') as csvfile:
                        writer = csv.writer(csvfile, delimiter=';')
                        writer.writerow(vars)

           
            

            
            
        
    

parser = argparse.ArgumentParser()
parser.add_argument('--start', type=int, default=2, help='start index')
parser.add_argument('--end', type=int, default=3, help='end index')
parser.add_argument('--model', type=str, default='openai/gpt-4-0314', help='model name')
parser.add_argument('--temperature', type=float, default=0, help='temperature')
parser.add_argument('--max_tokens', type=int, default=2000, help='max tokens')
# change num completions to 10
parser.add_argument('--num_completions', type=int, default=1, help='number of completions')
parser.add_argument('--num_shots', type=int, default=3, help='number of shots')
parser.add_argument('--num_stories', type=int, default=2, help='number of stories to generate')
parser.add_argument('--verbose', type=bool, default=True, help='verbose')
parser.add_argument('--api', type=str, default='azure', help='which api to use')

if __name__ == "__main__":
    args = parser.parse_args()
    gen_chat(args)