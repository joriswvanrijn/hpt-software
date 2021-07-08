from console import console
import __constants
from utils import show_error
import pandas as pd
import numpy as np 
import sys
import statistics
import os.path

def identify_gaps_in_gaze_positions(participant_id, progress, task):
    input_file_name = '../inputs/{}/merged_surfaces.csv'.format(participant_id)
    output_file_name = '../inputs/{}/merged_surfaces_with_gaps.csv'.format(participant_id)

    # Check if our input file exists
    if not os.path.isfile(input_file_name):
        show_error('Input file for step 2 is not found. Run step 1 first.', progress)

    df = pd.read_csv(input_file_name)

    # Set the total amount of jobs we're performing in this task
    progress.update(task, total=(len(df)-1 + 2))
    progress.print('[bold yellow]We are starting identifying gaps in {}'.format(input_file_name))

    # Rolling average of confidence to establish is_blink
    df['is_blink'] = False
    df['confidence_SMA'] = df['confidence'].rolling(window=3, center=True).mean()
    df.loc[(df['confidence_SMA'] < __constants.confidence_treshold), 'is_blink'] = True
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

    counter = 0

    progress.print('[bold yellow]We are starting to calculate the Simple Rolling Mediam for true_x_scaled and true_y_scaled. This may take a while.')

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