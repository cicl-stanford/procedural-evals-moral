from langchain.chat_models import AzureChatOpenAI
from typing import List
import os

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
            # azure_endpoint="https://philipp.openai.azure.com/",
            openai_api_version="2023-05-15",
            deployment_name='gpt-4',
            openai_api_key=os.getenv("API_KEY"),
            openai_api_type="azure",
            temperature=args.temperature,
        )
    else:
        raise Exception(f"Unknown API {args.api}")
    return llm

