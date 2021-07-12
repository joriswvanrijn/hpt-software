import __constants
from utils__general import show_error
import os.path
import subprocess
import json
import pandas as pd
from utils__aois import prepare_aios_df
import math
import numpy as np
from datetime import datetime
import sys

def generate_output(participant_id, rois_file, progress, task):
    progress.print("[bold yellow]We are starting generating output")

    input_file_name = '../outputs/{}/entries_exits.json'.format(participant_id)
    if not os.path.isfile(input_file_name):
        show_error('Input file for step 5 is not found. Run step 4 first.', progress)

    # Fetch all entries and exits
    a_file = open(input_file_name, "r")
    entries_and_exits = json.loads(a_file.read())

    # Perpare ROI's
    df_rois = pd.read_csv('../rois/{}'.format(rois_file))
    df_rois = prepare_aios_df(df_rois)

    # Set up the basics of the output file
    df = pd.DataFrame(columns = [
        'object_id',
        'first_appearance_time',
        'last_appearance_time',
        'total_appearance_duration',
        'total_dwell_duration',
    #     'first_entry',
        'total_diversion_duration',
        # more columns to come
    ])

    # Fill object ID
    df['object_id'] = (df_rois['Object ID'].unique().reshape(1, -1)[0])
    df = df.sort_values(['object_id'])
    df = df.reset_index()

    # First appearance time
    df_temp = df_rois.copy()
    df_temp = df_temp.drop_duplicates(['Object ID'], keep='first')
    df_temp = df_temp.sort_values(['Object ID'])
    df_temp = df_temp.reset_index(drop=True)
    df['first_appearance_time'] = df_temp['actual_time']

    # Last appearance time
    df_temp = df_rois.copy()
    df_temp = df_temp.drop_duplicates(['Object ID'], keep='last')
    df_temp = df_temp.sort_values(['Object ID'])
    df_temp = df_temp.reset_index(drop=True)
    df['last_appearance_time'] = df_temp['actual_time']

    # Total appearance duration
    df['total_appearance_duration'] = df['last_appearance_time'] - df['first_appearance_time']
    df['total_dwell_duration'] = 0

    # Round time values
    df = df.round({'first_appearance_time': 2, 'last_appearance_time': 2 })

    # Total appearance duration
    df['total_appearance_duration'] = df['last_appearance_time'] - df['first_appearance_time']
    df = df.round({'total_appearance_duration': 2})

        # First, set up all columns needed for entries and exist (and dwell time)
    longest_key = None
    longest_length = 0

    progress.advance(task)

    for roi, timestamps in entries_and_exits.items():
        if(longest_length < len(timestamps)):
            longest_key = roi
            longest_length = len(timestamps)

    progress.advance(task)

    sets_to_add = int(longest_length / 2)

    for i in range(sets_to_add):

        df['entry({})'.format(i + 1)] = None
        df['exit({})'.format(i + 1)] = None
        df['dwell_time({})'.format(i + 1)] = None

    progress.advance(task)

    # Populate all the entry(n) exit(n) and dwell_time(n) columns
    for roi, timestamps in entries_and_exits.items():

        for i in range(len(timestamps)):
            
            if i % 2 != 0:

                index = df.index[df['object_id'] == roi]

                n = math.ceil(i/2)
                entry_n = previous_timestamp = timestamps[i - 1]
                exit_n = current_timestamp = timestamps[i]
                dwell_time_n = exit_n - entry_n
                df.at[index, 'entry({})'.format(n)] = entry_n
                df.at[index, 'exit({})'.format(n)] = exit_n
                df.at[index, 'dwell_time({})'.format(n)] = dwell_time_n           

    progress.advance(task)

    # Add empty columns
    df['total_diversion_duration'] = 0

    # Remove short durations between exits and entries
    for i in range(sets_to_add):
        # for each set entry, exit, dwell
        n = i + 1
        if n > 1:
            for index, row in df.iterrows():
                # dur = duration_between_entry_and_previous_exit
                if row['entry({})'.format(n)] != None and row['exit({})'.format(n-1)] != None:
                    dur = row['entry({})'.format(n)] - row['exit({})'.format(n-1)]
                    
                    if(dur < __constants.minimal_treshold_entry_exit):
                        # replace the exit(n-1) with the exit(n)
                        df.at[index, 'exit({})'.format(n - 1)] = row['exit({})'.format(n)]
                        # take the sum of dwell(n-1) and dwell(n)
                        df.at[index, 'dwell_time({})'.format(n - 1)] = row['dwell_time({})'.format(n - 1)] + row['dwell_time({})'.format(n)]
                        df.at[index, 'entry({})'.format(n)] = None
                        df.at[index, 'exit({})'.format(n)] = None
                        df.at[index, 'dwell_time({})'.format(n)] = None

    progress.advance(task)

    # After that, filter short dwell_time(n)
    for i in range(sets_to_add):
        # for each set entry, exit, dwell
        n = i + 1
        if n > 1:
            for index, row in df.iterrows():
                if row['dwell_time({})'.format(n)] != None and row['dwell_time({})'.format(n)] < __constants.minimal_treshold_dwell:
                    df.at[index, 'entry({})'.format(n)] = None
                    df.at[index, 'exit({})'.format(n)] = None
                    df.at[index, 'dwell_time({})'.format(n)] = None

    progress.advance(task)

    # We are left with some NaN values, let's squeeze the rows
    def squeeze_nan(x):
        original_columns = x.index.tolist()
        squeezed = x.dropna()
        squeezed.index = [original_columns[n] for n in range(squeezed.count())]
        return squeezed.reindex(original_columns, fill_value=np.nan)

    # df = df.apply(squeeze_nan, axis=1)

    # Now, delete empty columns
    df.dropna(how='all', axis=1, inplace=True)

    progress.advance(task)

    # Calculate percentage dwell_duration/total_appearance
    # df['ratio_dwell_duration_total_appereance'] = df['total_dwell_duration']/df['total_appearance_duration']*100

    # Add tresholds to output
    df_w = df.append({
        'object_id': 'minimal_treshold_entry_exit = {}'.format(__constants.minimal_treshold_entry_exit),
        'first_appearance_time': 'minimal_treshold_dwell = {}'.format(__constants.minimal_treshold_dwell),
        'last_appearance_time': 'minimal_angle_of_aoi = {}'.format(__constants.minimal_angle_of_aoi),
        'total_appearance_duration': 'consecutive_0_treshold = {}'.format(__constants.consecutive_0_treshold)
    }, ignore_index=True)

    progress.advance(task)

    # Calculate dwell duration by getting the sum of dwell_duration
    df_w['total_dwell_duration'] = df_w.filter(regex='dwell_time\([\d]*\)',axis=1).sum(axis=1)

    # Write to csv
    output_file_name = '../outputs/{}/output_{}.csv'.format(participant_id, datetime.now().strftime("%Y_%m_%d-%H_%M_%S"))
    df_w.to_csv(output_file_name)

    progress.print("[green bold]Saved output to {}".format(output_file_name))

    subprocess.call(['open', output_file_name])
    
    progress.advance(task)