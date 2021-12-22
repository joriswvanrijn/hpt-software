import __constants
import pandas as pd
import numpy as np
from scipy.interpolate import PchipInterpolator
import matplotlib.pyplot as plt
import sys
import json

def to_lin_time_scale_and_generate_tsv(participant_id, video_id, progress, task):
    progress.print("[red]TODO: interpolate to linear time axis")
    progress.print("[red]TODO: generate TSV (x y)")

    input_file_name = '{}/{}/{}/merged_surfaces_with_gaps.csv'.format(
        __constants.input_folder, participant_id, video_id)

    output_file_name = '{}/{}/{}/linspaced_gaze_positions.csv'.format(
        __constants.input_folder, participant_id, video_id)
    
    output_file_name_tsv_with_nan = '{}/{}/{}/linspaced_gaze_positions.tsv'.format(
        __constants.input_folder, participant_id, video_id)

    # Read GP
    gp = pd.read_csv(input_file_name)

    # Change time scale to linear
    gp_with_nan = to_lin_time(progress, gp, output_file_name, participant_id, video_id)

    # controle stap
    # plt.plot(gp.actual_time, gp.true_x_scaled)
    # plt.plot(gazeInt.actual_time, gazeInt.x)
    # plt.show()

    # Generate a tsv file
    gp_with_nan[['x', 'y']].to_csv(output_file_name_tsv_with_nan, sep="\t", index=False, header=False)

    sys.exit()

def to_lin_time(progress, original_gp, output_file_name, participant_id, video_id):
    first_timestamp = original_gp.actual_time.iloc[0]  
    last_timestamp = original_gp.actual_time.iloc[-1] 
    
    # create gp df without nans (otherwise we cant interpolate)
    gp = original_gp[original_gp['true_x_scaled'].notna()] # NB: x and y are the same

    progress.print('First timestamp: {}'.format(first_timestamp))
    progress.print('Last timestamp: {}'.format(last_timestamp))
    
    progress.print('Average sample rate in data set: {}'.format(len(gp)/last_timestamp))

    # we find the new index
    timeIX = np.linspace(
        int(np.floor(first_timestamp)), 
        int(np.ceil(last_timestamp)), 
        int(np.ceil(last_timestamp - first_timestamp) * __constants.sample_rate_ET + 1)
    )
 
    def interp(x, y):
        f = PchipInterpolator(x, y, extrapolate=True)
        return f(timeIX)

    gazeInt = pd.DataFrame()
    gazeInt.loc[:, 'actual_time'] = timeIX

    gazeInt.loc[:, 'x'] = interp(gp.actual_time, gp.true_x_scaled)
    gazeInt.loc[:, 'y'] = interp(gp.actual_time, gp.true_y_scaled)

    # Now, check in the original dataframe where we have gaps
    # NaN the x,y in rows where we know there is a gap
    gap_timestamps_file = '../outputs/{}/{}/gap_timestamps.json'.format(participant_id, video_id)
    a_file = open(gap_timestamps_file, "r")
    gap_timestamps = json.loads(a_file.read())

    for timestamp in gap_timestamps:
        gazeInt.loc[(gazeInt['actual_time'] > timestamp[0]) & (gazeInt['actual_time'] < timestamp[1]), 'x'] = np.NaN
        gazeInt.loc[(gazeInt['actual_time'] > timestamp[0]) & (gazeInt['actual_time'] < timestamp[1]), 'y'] = np.NaN
        
    gazeInt.to_csv(output_file_name)

    return gazeInt