import __constants
import pandas as pd
import sys
import statistics

def apply_median_filter_on_coordinates(participant_id, video_id, progress, task):
    progress.print("[blue]Applying median filter on x and y")

    input_file_name = '{}/{}/{}/interpolated_gp.csv'.format(
        __constants.input_folder, participant_id, video_id)

    output_file_name = '{}/{}/{}/gp.csv'.format(
        __constants.input_folder, participant_id, video_id)

    df = pd.read_csv(input_file_name)

    # Is_valid_gap
    df['is_valid_gap'] = False
    df.loc[df['x'].isnull(), 'is_valid_gap'] = True

    # For debugging purposes:
    # print(df[['confidence', 'is_valid_gap', 'true_x_scaled', 'true_y_scaled']][df['is_valid_gap'] == True].head())

    progress.print('We have detected valid gaps')
    progress.advance(task)

    # Calculate the medians of the coordinates (window=3)
    # df['may_calculate_SRM'] = False
    df['x1'] = None
    df['y1'] = None

    progress.print('[bold yellow]We are starting to calculate the Simple Rolling Median for x and y. This may take a while.')

    progress.update(task, total=(len(df)-1+1))

    counter = 0
    for index, sample in df.iterrows():

        # Some nice progress output
        if(counter % 2000 == 0 or counter == 0):
            progress.print('[bold deep _pink4]Processed: {}/{}'.format(counter, len(df)))
        counter = counter + 1

        if(sample['is_valid_gap'] == False):

            # change this if we are changing window size > 3 
            if(index == 0 or index == df.shape[0] - 1):
                # for first and last row of dataset
                df.iloc[index, df.columns.get_loc('x')] = sample['x']
                df.iloc[index, df.columns.get_loc('y')] = sample['y']
                continue
        
            elif(df.at[index + 1, 'is_valid_gap'] == False and df.at[index - 1, 'is_valid_gap'] == False):
                # for all other rows
                df.iloc[index, df.columns.get_loc('x')] = statistics.median([
                    df.at[index - 1, 'x'],
                    df.at[index, 'x'],
                    df.at[index + 1, 'x'],
                ])
                df.iloc[index, df.columns.get_loc('y')] = statistics.median([
                    df.at[index - 1, 'y'],
                    df.at[index, 'y'],
                    df.at[index + 1, 'y'],
                ])

            else:
                df.iloc[index, df.columns.get_loc('x1')] = sample['x']
                df.iloc[index, df.columns.get_loc('y1')] = sample['y']

        progress.advance(task)

    # Write to csv
    progress.print('[bold green]Done! We saved gaze_positions.csv with {} rows'.format(len(df)))
    df.to_csv(output_file_name)