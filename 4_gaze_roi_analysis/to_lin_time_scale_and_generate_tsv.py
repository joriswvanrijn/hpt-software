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

    output_file_name = '{}/{}/{}/linspaced_gaze_positions.csv'.format(
        __constants.input_folder, participant_id, video_id)
    
    output_file_name_tsv = '{}/{}/{}/linspaced_gaze_positions.tsv'.format(
        __constants.input_folder, participant_id, video_id)

    # Read GP
    gp = pd.read_csv(input_file_name)

    first_timestamp = gp.actual_time.iloc[0]  
    last_timestamp = gp.actual_time.iloc[-1]  

    very_large_number = np.iinfo(np.intp).max

    gp['true_x_scaled'].fillna(very_large_number, inplace=True)
    gp['true_y_scaled'].fillna(very_large_number, inplace=True)

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
    gazeInt.loc[gazeInt['x'] > 20000, 'x'] = np.NaN
    gazeInt.loc[gazeInt['y'] > 20000, 'y'] = np.NaN
    gp.loc[gp['true_x_scaled'] == very_large_number, 'true_x_scaled'] = np.NaN
    gp.loc[gp['true_y_scaled'] == very_large_number, 'true_y_scaled'] = np.NaN

    gazeInt.to_csv(output_file_name)

    # controle stap
    # plt.plot(gp.actual_time, gp.true_x_scaled)
    # plt.plot(gazeInt.actual_time, gazeInt.x)
    # plt.show()

    # Generate a tsv file
    gazeInt[['x', 'y']].to_csv(output_file_name_tsv, sep="\t", index=False, header=False)

    sys.exit()