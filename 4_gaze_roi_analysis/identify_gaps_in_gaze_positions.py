import __constants
from utils__general import show_error
import pandas as pd
import numpy as np 
import sys
import statistics
import os.path

def identify_gaps_in_gaze_positions(participant_id, progress, task):
    input_file_name = '../inputs/{}/merged_surfaces.csv'.format(participant_id)
    output_file_name = '../inputs/{}/merged_surfaces_with_gaps.csv'.format(participant_id)
    input_file_name_blinks = '../inputs/{}/blinks.csv'.format(participant_id)

    # Check if our input file exists
    if not os.path.isfile(input_file_name):
        show_error('Input file for step 2 is not found. Run step 1 first.', progress)

    if not os.path.isfile(input_file_name_blinks):
        show_error('No blinks.csv found.', progress)

    df = pd.read_csv(input_file_name)

    # Set the total amount of jobs we're performing in this task
    progress.update(task, total=(len(df)-1 + 2))
    progress.print('[bold yellow]We are starting identifying gaps in {}'.format(input_file_name))

    # Use input blinks.csv to populate is_blink column
    df['is_blink'] = False
    blinks = pd.read_csv(input_file_name_blinks)

    for r, blink in blinks.iterrows():
        start = blink['start_timestamp'] - 0.1 #(100ms)
        end = blink['end_timestamp'] + 0.1 #(100ms)
        progress.print('Settings blinks between {} and {}'.format(start, end))        
        df.loc[(start <= df['gaze_timestamp']) & (end >= df['gaze_timestamp']), 'is_blink'] = True

    progress.print('Found {} rows which had to be set is_blink = True'.format(len(df[df['is_blink'] == True])))
    progress.print('We have detected blinks')
    progress.advance(task)

    # Is_valid_gap
    df['is_valid_gap'] = (df['on_screen'] == False) | df['is_blink']
    progress.print('We have detected valid gaps')
    progress.advance(task)

    # Calculate the medians of the coordinates (window=3)
    df['may_calculate_SRM'] = False
    df['true_x_scaled_SRM'] = None
    df['true_y_scaled_SRM'] = None

    progress.print('[bold yellow]We are starting to calculate the Simple Rolling Median for true_x_scaled and true_y_scaled. This may take a while.')

    counter = 0
    for index, sample in df.iterrows():

        # Some nice progress output
        if(counter % 2000 == 0 or counter == 0):
            progress.print('[bold deep_pink4]Processed: {}/{}'.format(counter, len(df)))
        counter = counter + 1

        if(sample['is_valid_gap'] == False):

            # change this if we are changing window size > 3 
            if(index == 0 or index == df.shape[0] - 1):
                # for first and last row of dataset
                df.iloc[index, df.columns.get_loc('true_x_scaled_SRM')] = sample['true_x_scaled']
                df.iloc[index, df.columns.get_loc('true_y_scaled_SRM')] = sample['true_y_scaled']
                continue
        
            elif(df.at[index + 1, 'is_valid_gap'] == False and df.at[index - 1, 'is_valid_gap'] == False):
                # for all other rows
                df.iloc[index, df.columns.get_loc('true_x_scaled_SRM')] = statistics.median([
                    df.at[index - 1, 'true_x_scaled'],
                    df.at[index, 'true_x_scaled'],
                    df.at[index + 1, 'true_x_scaled'],
                ])
                df.iloc[index, df.columns.get_loc('true_y_scaled_SRM')] = statistics.median([
                    df.at[index - 1, 'true_y_scaled'],
                    df.at[index, 'true_y_scaled'],
                    df.at[index + 1, 'true_y_scaled'],
                ])

            else:
                df.iloc[index, df.columns.get_loc('true_x_scaled_SRM')] = sample['true_x_scaled']
                df.iloc[index, df.columns.get_loc('true_y_scaled_SRM')] = sample['true_y_scaled']

        progress.advance(task)

    progress.print("Done! We will start outputting the dataframe to a csv file. This will take a second.")
    df.to_csv(output_file_name, index=False)
    progress.print('[bold green]We are done! The new csv is outputted to {} and contains {} rows.'.format(output_file_name, len(df)))