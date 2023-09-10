import random
import csv
import tqdm
import argparse
import ast

from langchain.chat_models import ChatOpenAI
from langchain.schema import (
    AIMessage,
    HumanMessage,
    SystemMessage
)
from crfm import crfmChatLLM

from utils import push_data, get_num_items, get_vars_from_out

letters = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L',
           'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W','X', 'Y', 'Z']
DATA_DIR = '../../data'
PROMPT_DIR = '../prompt_instructions'
WORDS_DIR = '../words'
REPO_URL = 'https://github.com/ayeshakhawaja/moral-judgment-prompt.git'
CSV_NAME = 'morality_stage_1'

parser = argparse.ArgumentParser()
parser.add_argument('--model', type=str, default='openai/gpt-4-0314', help='model name')
parser.add_argument('--temperature', type=float, default=0.5, help='temperature')
parser.add_argument('--max_tokens', type=int, default=2000, help='max tokens')
# change num completions to 10
parser.add_argument('--num_completions', type=int, default=1, help='number of completions')
parser.add_argument('--num_shots', type=int, default=3, help='number of shots')
parser.add_argument('--num_stories', type=int, default=2, help='number of stories to generate')
parser.add_argument('--verbose', action='store_true', help='verbose')


def get_llm(args):
    llm = crfmChatLLM(
        model_name=args.model,
        temperature=args.temperature,
        max_tokens=args.max_tokens,
        num_completions=args.num_completions,
        request_timeout=180
    )
    return llm

def get_human_message(args):
    letter_name, letter_profession = random.choice(letters), random.choice(letters)

    with(open(f'{PROMPT_DIR}/reminder_stage_1.txt', 'r')) as f:
        msg = f.read().strip()

    msg = msg.replace("[name_letter]", letter_name)
    msg = msg.replace("[profession_letter]", letter_profession)

    return msg


def gen_chat(args):
    response_template = """Here is the story:
Context: {context}
Situation CC: {cc}
Harm CC: {harm_cc}
Good CC: {good_cc}
Action CC: {action_cc}
Prevention CC: {prevention_cc}
External Cause CC: {external_cause_cc}
Situation CoC: {coc}
Good CoC: {good_coc}
Harm CoC: {harm_coc}
Action CoC: {action_coc}
Prevention CoC: {prevention_coc}
External Cause CoC: {external_cause_coc}
"""

    llm = get_llm(args)
    with(open(f'{PROMPT_DIR}/morality_stage_1.txt', 'r')) as f:
        instruction_text = f.read()

    system_message = SystemMessage(content=instruction_text)
    # 2-shots by default
    human_message_0 = HumanMessage(content='Generate a story')
    s = get_human_message(args)
    new_message = s.split("Story (the")
    human_message_1 = HumanMessage(content=new_message[0])
    
    examples = []
    template_var = ["context", "cc", "harm_cc", "good_cc", "action_cc", "prevention_cc", "external_cause_cc", "coc", "good_coc", "harm_coc", "action_coc", "prevention_coc", "external_cause_coc"]
    csv_file = f'{DATA_DIR}/{CSV_NAME}.csv'

    prompt_tokens_used = 0
    completion_tokens_used = 0

    # run loop with n stories, increase by num_completions
    for n_story in tqdm.tqdm(range(0, args.num_stories, args.num_completions)):
        s = get_human_message(args)
        new_message = s.split("Story (the")
        human_message_1 = HumanMessage(content=new_message[0])
   
        # read examples from csv file every iteration to add generated samples to the pool of seed examples
        if args.verbose:
            print(f"Reading examples from {csv_file} with existing {get_num_items(csv_file)} examples")
        # read a few examples from the csv file
        with open(csv_file, 'r') as f:
            for line in f.readlines():
                params = line.split(';')
                example = {k: params[v].strip() for v, k in enumerate(template_var)} 
                examples.append(example)
        random.shuffle(examples)

        # 2-shots by default	
        messages = [system_message]	
        for i in range(args.num_shots):	
            messages.append(human_message_0)

            messages.append(AIMessage(content=response_template.format(**examples[i])))	
        messages.append(human_message_1)	
        if args.verbose:
            print(f"------ messages ------")	
            print(messages)	
        responses = llm.generate([messages], stop=["System:"])
        # prompt_tokens_used += responses.llm_output['token_usage']['prompt_tokens']
        # completion_tokens_used += responses.llm_output['token_usage']['completion_tokens']
        # price = (prompt_tokens_used * 0.03 + completion_tokens_used * 0.06) / 1000.
        # update tqdm progress bar with price
        # tqdm.tqdm.write(f"Price: {price:.2f} USD, Price per story: {price/(n_story+args.num_completions):.2f} USD")
        for g, generation in enumerate(responses.generations[0]):
            # print(f"AYESHA LOOK HERE \n: {generation.text}")
            if args.verbose:
                print(f"------ Generated Story {n_story+g} ------")
                print(generation.text)
                print("------------ Fin --------------")
            list_var = ["Context", "Situation CC", "Harm CC", "Good CC", "Action CC", "Prevention CC", "External Cause CC", "Situation CoC", "Good CoC", "Harm CoC", "Action CoC", "Prevention CoC", "External Cause CoC"]
            try:
                out_vars = get_vars_from_out(generation.text, list_var)
                # breakpoint()
            except:
                print("Error in parsing output")
                breakpoint()
            data = [out_vars[k] for k in list_var]
            story_file = f'{DATA_DIR}/{CSV_NAME}.csv'
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
