import __constants
from utils__general import show_error
import pandas as pd
import numpy as np 
import sys
import statistics
import os.path

def identify_gaps_in_gaze_positions(participant_id, video_id, progress, task):
    # ✅ Don't remove rows, only NaN them (off screen and below confidence of .8)
    # ✅ if gap duration < 60ms -> interpolate NaN
    # ✅ if gap duration > 60ms -> NaN them

    # EVENT detection
    # TODO: interpoleren to linear time axis
    # TODO: generate TSV (x y)

    input_file_name = '{}/{}/{}/merged_surfaces.csv'.format(
        __constants.input_folder, participant_id, video_id)

    output_file_name = '{}/{}/{}/merged_surfaces_with_gaps.csv'.format(
        __constants.input_folder, participant_id, video_id)
    
    # Check if our input file exists
    if not os.path.isfile(input_file_name):
        show_error('Input file for step 2 is not found. Run step 1 first.', progress)

    df = pd.read_csv(input_file_name)

    # Set X and Y to NaN when confidence < treshold
    df.loc[df['confidence'] < __constants.confidence_treshold, 'true_x_scaled'] = np.NaN
    df.loc[df['confidence'] < __constants.confidence_treshold, 'true_y_scaled'] = np.NaN
    
    # TODO: output text file stating how many X,Y's were changed to NaN

    # Set X and Y to NaN when not looking on screen
    df.loc[df['on_screen'] == False, 'true_x_scaled'] = np.NaN
    df.loc[df['on_screen'] == False, 'true_y_scaled'] = np.NaN

    # For debugging purposes:
    # print(df[['confidence', 'on_screen', 'true_x_scaled', 'true_y_scaled']][df['on_screen'] == False].head())
    # print(df[['confidence', 'on_screen', 'true_x_scaled', 'true_y_scaled']][df['confidence'] < __constants.confidence_treshold].head())

    # TODO: output text file stating how many X,Y's were changed to NaN
    # May use this:
    # progress.print('{} in original DF '.format(len(df)))
    # progress.print('{} in dfAboveTreshold '.format(len(dfAboveTreshold)))
    # progress.print('{} rows removed due to conf < .8 '.format( len(df) - len(dfAboveTreshold) ))
    # progress.print('[bold red] {}% percent of rows removed due to conf < .8 '.format(
    #     round((len(df) - len(dfAboveTreshold))/len(df), 2) * 100
    # ))
 
    progress.advance(task)

    # Interpolate x and y if the time gaps are < treshold (60 ms)
    df = df.reset_index()
    counter = 0
    currentlyAtGap = False
    currentGapStartedAtIndex = np.NaN
    durationOfCurrentGap = 0

    for index, gp in df.iterrows():
        if(index % 2000 == 0 or index == 0):
            progress.print('[bold deep_pink4]Processed: {}/{}'.format(index, len(df)))

        # Open gap
        if(np.isnan(gp['true_x_scaled']) and np.isnan(gp['true_y_scaled']) and not currentlyAtGap):
            # progress.print('[blue]Opened a gap at index: {}'.format(index))
            currentGapStartedAtIndex = index
            currentlyAtGap = True
        
        # Decide on gap duration
        currentlyAtLastGazeP = (index == len(df) - 1)
        if(currentlyAtGap and not currentlyAtLastGazeP):
            durationOfCurrentGazeP = df.loc[index + 1, 'actual_time'] - gp['actual_time']
            durationOfCurrentGap = durationOfCurrentGap + durationOfCurrentGazeP

        # Close and interpolate gap
        if(not np.isnan(gp['true_x_scaled']) and not np.isnan(gp['true_y_scaled']) and currentlyAtGap):
            # progress.print('Closed a gap at index: {}, with duration: {}s'.format(index, durationOfCurrentGap))
            # progress.print('Should we interpolate between index {} and index {}?'.format(currentGapStartedAtIndex, index))

            if(durationOfCurrentGap < __constants.interpolate_if_gap_shorter_than):
                # progress.print('[blue]Yes, we should interpolate. Do that now:')

                # progress.print('Interpolate X, between: {} and {}'.format(start_x, end_x))
                # progress.print('Interpolate Y, between: {} and {}'.format(start_y, end_y))

                # Interpolate x
                df.loc[(currentGapStartedAtIndex - 1):index, 'true_x_scaled'] = df.loc[(currentGapStartedAtIndex - 1):index, 'true_x_scaled'].interpolate()
                # Interpolate y
                df.loc[(currentGapStartedAtIndex - 1):index, 'true_y_scaled'] = df.loc[(currentGapStartedAtIndex - 1):index, 'true_y_scaled'].interpolate()

                # For debugging purposes
                # print(df.loc[(currentGapStartedAtIndex - 1):index, ['confidence', 'on_screen', 'true_x_scaled', 'true_y_scaled']].head())

            # Reset
            currentlyAtGap = False
            durationOfCurrentGap = 0
            currentGapStartedAtIndex = np.NaN

    progress.print("Done! We will start outputting the dataframe to a csv file. This will take a second.")
    df.to_csv(output_file_name, index=False)
    progress.print('[bold green]We are done! The new csv is outputted to {} and contains {} rows.'.format(output_file_name, len(df)))

    sys.exit()

    # We commented this section below on 21 oct
    # since can't calculate the SRM in this way anymore since we remove gaps due to blinks (conf < .8) or of screen
    # instead of thinking of a new method to calulate SRM, we assume that it's not needed anymore

    # # Is_valid_gap
    # df['is_valid_gap'] = (df['on_screen'] == False)
    # progress.print('We have detected valid gaps')
    # progress.advance(task)

    # # Calculate the medians of the coordinates (window=3)
    # df['may_calculate_SRM'] = False
    # df['true_x_scaled_SRM'] = None
    # df['true_y_scaled_SRM'] = None

    # progress.print('[bold yellow]We are starting to calculate the Simple Rolling Median for true_x_scaled and true_y_scaled. This may take a while.')

    # counter = 0
    # for index, sample in df.iterrows():

    #     # Some nice progress output
    #     if(counter % 2000 == 0 or counter == 0):
    #         progress.print('[bold deep _pink4]Processed: {}/{}'.format(counter, len(df)))
    #     counter = counter + 1

    #     if(sample['is_valid_gap'] == False):

    #         # change this if we are changing window size > 3 
    #         if(index == 0 or index == df.shape[0] - 1):
    #             # for first and last row of dataset
    #             df.iloc[index, df.columns.get_loc('true_x_scaled_SRM')] = sample['true_x_scaled']
    #             df.iloc[index, df.columns.get_loc('true_y_scaled_SRM')] = sample['true_y_scaled']
    #             continue
        
    #         elif(df.at[index + 1, 'is_valid_gap'] == False and df.at[index - 1, 'is_valid_gap'] == False):
    #             # for all other rows
    #             df.iloc[index, df.columns.get_loc('true_x_scaled_SRM')] = statistics.median([
    #                 df.at[index - 1, 'true_x_scaled'],
    #                 df.at[index, 'true_x_scaled'],
    #                 df.at[index + 1, 'true_x_scaled'],
    #             ])
    #             df.iloc[index, df.columns.get_loc('true_y_scaled_SRM')] = statistics.median([
    #                 df.at[index - 1, 'true_y_scaled'],
    #                 df.at[index, 'true_y_scaled'],
    #                 df.at[index + 1, 'true_y_scaled'],
    #             ])

    #         else:
    #             df.iloc[index, df.columns.get_loc('true_x_scaled_SRM')] = sample['true_x_scaled']
    #             df.iloc[index, df.columns.get_loc('true_y_scaled_SRM')] = sample['true_y_scaled']

    #     progress.advance(task)
