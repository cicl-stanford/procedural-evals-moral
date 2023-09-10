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

DATA_DIR = '../../data'
PROMPT_DIR = '../prompt_instructions'
REPO_URL = 'https://github.com/ayeshakhawaja/moral-judgment-prompt.git'
CSV_NAME_LOAD = 'morality_stage_1'
CSV_NAME_SAVE = 'morality_stage_2'

parser = argparse.ArgumentParser()
parser.add_argument('--model', type=str, default='openai/gpt-4-0314', help='model name')
parser.add_argument('--temperature', type=float, default=0.05, help='temperature')
parser.add_argument('--max_tokens', type=int, default=2000, help='max tokens')
# change num completions to 10
parser.add_argument('--num_completions', type=int, default=1, help='number of completions')
parser.add_argument('--num_shots', type=int, default=1, help='number of shots')
parser.add_argument('--num_stories', type=int, default=1, help='number of stories to generate')
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

def get_system_message(args):
    with(open(f'{PROMPT_DIR}/morality_stage_2.txt', 'r')) as f:
        msg = f.read().strip()
    if args.verbose: print(msg)
    scenario = """Context: {context}
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
External Cause CoC: {external_cause_coc}""" 
    msg = msg.format(scenario=scenario)
    return msg, scenario


def gen_chat(args):
    response_template = """
Scenario: {context}
Evitable Action CC: {evitable_action_cc}
Inevitable Action CC: {inevitable_action_cc}
Evitable Prevention CC: {evitable_prevention_cc}
Inevitable Prevention CC: {inevitable_prevention_cc}
Action CC: {action_cc}
Prevention CC: {prevention_cc}
Evitable Action CoC: {evitable_action_coc}
Inevitable Action CoC: {inevitable_action_coc}
Evitable Prevention CoC: {evitable_prevention_coc}
Inevitable Prevention CoC: {inevitable_prevention_coc}
Action CoC: {action_coc}
Prevention CoC: {prevention_coc}"""

    llm = get_llm(args)
    s, scenario_template = get_system_message(args)
    system_message = SystemMessage(content=s)

    with(open(f'{PROMPT_DIR}/example_scenario.txt', 'r')) as f:
        scenario = f.read().strip()
    human_message_0 = HumanMessage(content="Here is a scenario\n" + scenario)
    with (open(f'{PROMPT_DIR}/example_completion.txt', 'r')) as f:
        completion = f.read().strip()
    assistant_message_0 = AIMessage(content=completion)
    csv_file = f'{DATA_DIR}/{CSV_NAME_LOAD}.csv'
    scenario_var = ["context", "cc", "harm_cc", "good_cc", "action_cc", "prevention_cc", "external_cause_cc", "coc", "good_coc", "harm_coc", "action_coc", "prevention_coc", "external_cause_coc"]
    with(open(f'{PROMPT_DIR}/reminder_stage_2.txt', 'r')) as f:
        reminder = f.read().strip()
    with open(csv_file, 'r') as f:
        # read lines
        for line in tqdm.tqdm(f.readlines()[14:]):
            params = line.split(';')
            completion = {k: params[v].strip() for v, k in enumerate(scenario_var)}
            completion_prompt = scenario_template.format(**completion)
            human_message_1 = HumanMessage(content="Here is another scenario\n" + completion_prompt + "\n" + "REMINDER:\n" + reminder)
            messages = [system_message, human_message_0, assistant_message_0, human_message_1]
            print(messages)
            response = llm.generate([messages], stop=["System:"])

            for g, generation in enumerate(response.generations[0]):
                if args.verbose:
                    print(f"------ Generated Completion ------")
                    print(generation.text)
                list_var = ["Evitable Action CC", "Inevitable Action CC", "Evitable Prevention CC", "Inevitable Prevention CC", "Action CC", "Prevention CC", "Evitable Action CoC", "Inevitable Action CoC", "Evitable Prevention CoC", "Inevitable Prevention CoC", "Action CoC", "Prevention CoC"]
                try:
                    out_vars = get_vars_from_out(generation.text, list_var)
                except:
                    print("Error in parsing output")
                data = [out_vars[k] for k in list_var]
                data += ["auto", 0]
                story_file = f'{DATA_DIR}/{CSV_NAME_SAVE}.csv'
                with open(story_file, 'a') as csvfile:
                    writer = csv.writer(csvfile, delimiter=';')
                    writer.writerow(data)
                # breakpoint()
    
if __name__ == "__main__":
    args = parser.parse_args()
    # print(f"Generating {args.num_stories} stories")
    # if args.verbose:
    #     print(args)
    gen_chat(args)
