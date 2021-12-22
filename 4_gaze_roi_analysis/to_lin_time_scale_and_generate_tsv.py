import __constants
import pandas as pd
import numpy as np
from scipy.interpolate import PchipInterpolator
import matplotlib.pyplot as plt
import sys

def to_lin_time_scale_and_generate_tsv(participant_id, video_id, progress, task):
    progress.print("[red]TODO: interpolate to linear time axis")
    progress.print("[red]TODO: generate TSV (x y)")

    input_file_name = '{}/{}/{}/merged_surfaces_with_gaps.csv'.format(
        __constants.input_folder, participant_id, video_id)

    output_file_name_with_nan = '{}/{}/{}/linspaced_gaze_positions_with_nan.csv'.format(
        __constants.input_folder, participant_id, video_id)

    output_file_name_without_nan = '{}/{}/{}/linspaced_gaze_positions_without_nan.csv'.format(
        __constants.input_folder, participant_id, video_id)
    
    output_file_name_tsv_with_nan = '{}/{}/{}/linspaced_gaze_positions_with_nan.tsv'.format(
        __constants.input_folder, participant_id, video_id)

    output_file_name_tsv_without_nan = '{}/{}/{}/linspaced_gaze_positions_without_nan.tsv'.format(
        __constants.input_folder, participant_id, video_id)

    # Read GP
    gp = pd.read_csv(input_file_name)

    # Change time scale to linear, try to match NaN's (keep them in final data set)
    gp_with_nan = to_lin_time(progress, gp, output_file_name_with_nan, keepNaN=True)

    # Change time scale to linear, interpolate ALL gaps (so we're left with no NaN's)
    gp_without_nan = to_lin_time(progress, gp, output_file_name_without_nan, keepNaN=False)

    # controle stap
    # plt.plot(gp.actual_time, gp.true_x_scaled)
    # plt.plot(gazeInt.actual_time, gazeInt.x)
    # plt.show()

    # Generate a tsv file
    gp_with_nan[['x', 'y']].to_csv(output_file_name_tsv_with_nan, sep="\t", index=False, header=False)
    gp_without_nan[['x', 'y']].to_csv(output_file_name_tsv_without_nan, sep="\t", index=False, header=False)

    # Compare both tsv's
    differences = gp_with_nan.compare(gp_without_nan)
    differences = differences.reset_index()
    print(differences)

    sys.exit()

def to_lin_time(progress, gp, output_file_name, keepNaN=True):
    first_timestamp = gp.actual_time.iloc[0]  
    last_timestamp = gp.actual_time.iloc[-1]  

    very_large_number = np.iinfo(np.intp).max

    if(keepNaN):
        gp['true_x_scaled'].fillna(very_large_number, inplace=True)
        gp['true_y_scaled'].fillna(very_large_number, inplace=True)
    else:
        gp = gp[gp['true_x_scaled'].notna()] # NB: x and y are the same

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

    # Set all high x/y values to NaN again
    if(keepNaN):
        gazeInt.loc[gazeInt['x'] > 20000, 'x'] = np.NaN
        gazeInt.loc[gazeInt['y'] > 20000, 'y'] = np.NaN
        gp.loc[gp['true_x_scaled'] == very_large_number, 'true_x_scaled'] = np.NaN
        gp.loc[gp['true_y_scaled'] == very_large_number, 'true_y_scaled'] = np.NaN

    gazeInt.to_csv(output_file_name)

    return gazeInt