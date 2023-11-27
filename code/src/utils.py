import os
import csv
from subprocess import Popen, PIPE
import itertools
import pandas as pd
from langchain.chat_models import ChatOpenAI, AzureChatOpenAI
# from crfm import crfmChatLLM


def push_data(data_dir: str, repo_url: str):

    # Get the current working directory
    cwd = os.getcwd()

    # Change the working directory to the data directory
    os.chdir(data_dir)

    # pull changes from GitHub
    p = Popen(['git', 'pull'], stdout=PIPE, stderr=PIPE) # needs to be '.' to add all files from data directory
    p.communicate()

    # Stage all changes (can send them somwhere better than github i guess?)
    p = Popen(['git', 'add', '.'], stdout=PIPE, stderr=PIPE) # needs to be '.' to add all files from data directory
    p.communicate()

    # Commit changes
    p = Popen(['git', 'commit', '-m', 'auto-commit-csv-change'], stdout=PIPE, stderr=PIPE)
    p.communicate()

    # Push changes to GitHub
    p = Popen(['git', 'push', repo_url], stdout=PIPE, stderr=PIPE)
    p.communicate()

    # Change back to the original working directory
    os.chdir(cwd)

def edit_csv_row(filename, row_to_edit, new_data):
    if not os.path.exists(filename):
        raise Exception('No csv file found', filename)
    # Read the CSV file and store the data in a list
    with open(filename, 'r') as csvfile:
        reader = csv.reader(csvfile, delimiter=';')
        data = [row for row in reader]

    # Update the data in the desired row
    if len(data) > row_to_edit:
        data[row_to_edit] = new_data
    else:
        assert row_to_edit == len(data)
        data.append(new_data)

    # Write the updated data back to the CSV file
    print('writing to', filename)
    with open(filename, 'w') as csvfile:
        writer = csv.writer(csvfile, delimiter=';')
        writer.writerows(data)


def get_num_items(file_name: str) -> int:
    # Open the CSV file in append mode
    csv_file = f'{file_name}'
    if not os.path.exists(csv_file):
        return 0
    df = pd.read_csv(csv_file)
    return len(df)

def get_vars_from_out(out:str) -> dict[str, str]:
    var_dict = {}
    out = out.split('\n')
    out = [l for l in out if ':' in l and 'Agent' not in l]
    for line in out:
        elems = line.split(': ')
        if 'Inevitable' in elems[0]:
            elems[1] = elems[1].replace(' anyways', '')
        if len(elems) < 2:
            continue
        var_dict[elems[0]] = elems[1].strip()
    return var_dict

def get_llm(args):

    llm = None
 
    if args.api == 'azure':

        llm = AzureChatOpenAI(
            openai_api_base=os.getenv("BASE_URL"),
            openai_api_version="2023-05-15",
            deployment_name='gpt-4',
            openai_api_key=os.getenv("API_KEY"),
            openai_api_type="azure",
            temperature=args.temperature,
        )
    # else:
    #     llm = crfmChatLLM(
    #         model_name=args.model,
    #         temperature=args.temperature,
    #         max_tokens=args.max_tokens,
    #         num_completions=args.num_completions,
    #         request_timeout=180
    #     )

    return llm