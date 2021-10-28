import pandas as pd
import glob, os
import platform
import subprocess

output_folder = '../outputs/'
output_files = '*.csv'

participant_folders = glob.glob("{}/*/".format(output_folder))

dfs = []

for participant in participant_folders:
    folder = "{}{}/Deel1/*.csv".format(output_folder, participant)
    list_of_files = glob.glob(folder) # * means all if need specific format then *.csv
    print(folder)

    latest_file = max(list_of_files, key=os.path.getctime)
    print('added {}'.format(latest_file))
    df = pd.read_csv(latest_file)
    df['participant_id'] = participant.replace(output_folder, '').replace('/', '')
    dfs.append(df)

big_frame = pd.concat(dfs, ignore_index=True)
big_frame = big_frame.drop(columns=['Unnamed: 0', 'index'])

output_file_name = '{}merged_outputs.csv'.format(output_folder)
big_frame.to_csv(output_file_name)

if not platform.system() == 'Windows':
        subprocess.call(['open', output_file_name])