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

