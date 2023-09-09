import csv 

DATA_DIR = '../../data'
REPO_URL = 'https://github.com/ayeshakhawaja/moral-judgment-prompt.git'
CSV_NAME = 'morality'
CSV_NAME_STAGE_1 = 'morality_stage_1'
CSV_NAME_STAGE_2 = 'morality_stage_2'

# load both stages and stich each line together separated by; and write to new csv in same format
def stich_csv():
    with open(f'{DATA_DIR}/{CSV_NAME_STAGE_1}.csv', 'r') as f:
        reader = csv.reader(f, delimiter=";")
        stage_1 = list(reader)
    with open(f'{DATA_DIR}/{CSV_NAME_STAGE_2}.csv', 'r') as f:
        reader = csv.reader(f, delimiter=";")
        stage_2 = list(reader)
    with open(f'{DATA_DIR}/{CSV_NAME}.csv', 'w') as f:
        writer = csv.writer(f, delimiter=";")
        for i in range(len(stage_1)):
            writer.writerow(stage_1[i] + stage_2[i])

if __name__ == '__main__':
    stich_csv()