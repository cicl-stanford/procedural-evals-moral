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


def get_example(condition, rand_item):

    vars = {k: None for k in range(100)}
    if condition == "CC":
        with open(f'{PROMPT_DIR}/cc_stage_2.csv', 'r') as f:
            reader = csv.reader(f, delimiter=';')
            for i, row in enumerate(reader):
                if i == rand_item:
                    for j, elem in enumerate(row):
                        vars[j] = elem.strip()
                    break
        return f"""Context: {vars[0]}
Action Opportunity: {vars[1]}
Harm CC: {vars[2]}
Good CC: {vars[3]}
Preventable Cause CC: {vars[4]}
Non-Preventable Cause CC: {vars[5]}
"As a means to" CC: {vars[6]}
Evitable Action CC: {vars[7]}
Inevitable Action CC: {vars[8]}
Evitable Prevention CC: {vars[9]}
Inevitable Prevention CC: {vars[10]}
Action CC: {vars[11]}
Prevention CC: {vars[12]}"""

    elif condition == "CoC":
        with open(f'{PROMPT_DIR}/coc_stage_2.csv', 'r') as f:  
            reader = csv.reader(f, delimiter=';')
            for i, row in enumerate(reader):
                if i == rand_item:
                    for j, elem in enumerate(row):
                        vars[j] = elem.strip()
                    break
        return f"""Context: {vars[0]}
Action Opportunity: {vars[1]}
Harm CoC: {vars[2]}
Good CoC: {vars[3]}
Preventable Cause CoC: {vars[4]}
Non-Preventable Cause CoC: {vars[5]}
"As a side effect" CoC: {vars[6]}
Evitable Action CoC: {vars[7]}
Inevitable Action CoC: {vars[8]}
Evitable Prevention CoC: {vars[9]}
Inevitable Prevention CoC: {vars[10]}
Action CoC: {vars[11]}
Prevention CoC: {vars[12]}"""
                
            
def gen_chat(args, condition):
    llm = get_llm(args)
    
    vars = {k: None for k in range(100)}
    # TODO COMPLETE THIS

    

            # messages sent to model 
            messages = []
            if condition == "CC":
                with(open(f'{PROMPT_DIR}/cc_stage_2_severe.txt', 'r')) as f:
                    system_prompt = f.read().strip()
            elif condition == "CoC":
                with(open(f'{PROMPT_DIR}/coc_stage_2_severe.txt', 'r')) as f:
                    system_prompt = f.read().strip()

            example = get_example(condition, rand_item)

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
            breakpoint()
            responses = llm.generate([messages], stop=["System:"])


            for g, generation in enumerate(responses.generations[0]):
                if args.verbose:
                    print(f"------ Generated Story ------")
                    print(generation.text)
                    print("------------ Fin --------------")

                breakpoint()
                vars = get_vars_from_out(generation.text)
                if len(vars) == 6:
                    vars = vars[1:]
    
                if condition == "CC":
                    with open(f'{PROMPT_DIR}/cc_stage_2_severe.csv', 'a') as csvfile:
                        writer = csv.writer(csvfile, delimiter=';')
                        writer.writerow(vars)
                elif condition == "CoC":
                    with open(f'{PROMPT_DIR}/coc_stage_2_severe.csv', 'a') as csvfile:
                        writer = csv.writer(csvfile, delimiter=';')
                        writer.writerow(vars)

           
            

            
            
            


       
    

parser = argparse.ArgumentParser()
parser.add_argument('--start', type=int, default=2, help='start index')
parser.add_argument('--end', type=int, default=3, help='end index')
parser.add_argument('--model', type=str, default='openai/gpt-4-0314', help='model name')
parser.add_argument('--temperature', type=float, default=0.1, help='temperature')
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