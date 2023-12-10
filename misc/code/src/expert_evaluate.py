import os
import csv
import random

from flask import Flask, render_template, request

# from gen_fns import 
from utils import push_data, get_num_items, edit_csv_row

app = Flask(__name__)
DATA_DIR = '../../data'
VARS = ['context', 'cc', 'harm_cc', 'good_cc', 'action_cc', 'prevention_cc', 'external_cause_cc', 'coc', 
        'good_coc', 'harm_coc', 'action_coc', 'prevention_coc', 'external_cause_coc', 'evitable_action_cc',
        'inevitable_action_cc', 'evitable_prevention_cc', 'inevitable_prevention_cc', 'action_sentence_coc',
        'prevention_sentence_cc', 'evitable_action_coc', 'inevitable_action_coc', 'evitable_prevention_coc',
        'inevitable_prevention_coc', 'action_sentence_coc', 'prevention_sentence_coc']

# get index
@app.route('/')
def index():
    return render_template('expert_evaluate.html')


def get_num_stories(name):
    num_stories = get_num_items(f'{DATA_DIR}/ratings/{name}.csv')
    return num_stories


def get_stories(evaluator):
    eval_file = f'{DATA_DIR}/ratings/{evaluator}.csv'
    if os.path.exists(eval_file):
        # get the id of the last story rated
        with open(eval_file, 'r') as f:
            lines = list(csv.reader(f, delimiter=';'))
        idx = sum([1 for l in lines if len(l)==2])
    else:
        idx = 0
    
    story_dict = {}
    story_file = f'{DATA_DIR}/morality_v2.csv'
    if not os.path.exists(story_file):
        raise Exception('No context file found')
    with open(story_file, 'r') as f:
        stories = list(csv.reader(f, delimiter=';'))
    if idx >= len(stories):
        raise Exception('No more stories to rate')
    
    for i in range(len(stories[idx])):
        story_dict[vars[i]] = stories[idx][i]
        
    return story_dict, idx

# load story
@app.route('/load_story', methods=['POST'])
def load():
    evaluator = request.form['evaluator']
    data, idx = get_stories(evaluator)
    data['row'] = idx
    data['num_stories'] = get_num_stories(request.form['evaluator'])
    return data

# save data
@app.route('/store', methods=['POST'])
def store():
    evaluator = request.form['evaluator']
    row = int(request.form['row'])
    story_file = f'{DATA_DIR}/morality_v2.csv'
    with open(story_file, 'r') as f:
        stories = list(csv.reader(f, delimiter=';'))
        story = stories[row]
    
    edit_csv_row(story_file, row, story)
    data = [request.form.get(f) for f in ["story_structure", "behavior_evaluation"]]
    eval_csv = f'{DATA_DIR}/ratings/{evaluator}.csv'
    row = int(request.form.get('row'))
    edit_csv_row(eval_csv, row, data)
    data = {}
    data, idx = get_stories(evaluator)
    data['row'] = idx
    data['num_stories'] = get_num_stories(request.form.get('evaluator'))
    # Auto push the data to GitHub
    # push_data(DATA_DIR, REPO_URL)
    return data


if __name__ == '__main__':
    app.run(debug=True)