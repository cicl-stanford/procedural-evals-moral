import os
import csv
import random

from flask import Flask, render_template, request

# from gen_fns import 
from utils import push_data, get_num_items, edit_csv_row

app = Flask(__name__)
DATA_DIR = '../../data'

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
    story_dict['context'] = stories[idx][0]
    story_dict['cc'] = stories[idx][1]
    story_dict['harm_cc'] = stories[idx][2]
    story_dict['good_cc'] = stories[idx][3]
    story_dict['action_cc'] = stories[idx][4]
    story_dict['prevention_cc'] = stories[idx][5]
    story_dict['external_cause_cc'] = stories[idx][6]
    story_dict['coc'] = stories[idx][7]
    story_dict['good_coc'] = stories[idx][8]
    story_dict['harm_coc'] = stories[idx][9]
    story_dict['action_coc'] = stories[idx][10]
    story_dict['prevention_coc'] = stories[idx][11]
    story_dict['external_cause_coc'] = stories[idx][12]
    story_dict['evitable_action_cc'] = stories[idx][13]
    story_dict['inevitable_action_cc'] = stories[idx][14]
    story_dict['evitable_prevention_cc'] = stories[idx][15]
    story_dict['inevitable_prevention_cc'] = stories[idx][16]
    story_dict['action_sentence_cc'] = stories[idx][17]
    story_dict['prevention_sentence_cc'] = stories[idx][18]
    story_dict['evitable_action_coc'] = stories[idx][19]
    story_dict['inevitable_action_coc'] = stories[idx][20]
    story_dict['evitable_prevention_coc'] = stories[idx][21]
    story_dict['inevitable_prevention_coc'] = stories[idx][22]
    story_dict['action_sentence_coc'] = stories[idx][23]
    story_dict['prevention_sentence_coc'] = stories[idx][24]    
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