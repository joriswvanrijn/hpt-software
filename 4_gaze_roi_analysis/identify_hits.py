import __constants
import pandas as pd
from utils__aois import prepare_aios_df
from utils__margin_calculator import correct_aoi
import numpy as np
from utils__general import show_error
import os.path

def identify_hits(participant_id, rois_file, progress, task):
    progress.print("[bold yellow]We are starting identifying hits")

    # Perpare ROI's
    df_rois = pd.read_csv('../rois/{}'.format(rois_file))
    df_rois = prepare_aios_df(df_rois)

    # Check if our input file exists
    input_file_name = '../inputs/{}/merged_surfaces_with_gaps.csv'.format(participant_id)
    if not os.path.isfile(input_file_name):
        show_error('Input file for step 3 is not found. Run step 2 first.', progress)

    # Prepare merged surfaces with gaps
    df_gps = pd.read_csv(input_file_name)
    progress.print('found {} gaze position records'.format(len(df_gps)))

    df_gps['actual_time'] = df_gps['gaze_timestamp'] - abs(df_gps.loc[0, 'gaze_timestamp'])
    df_gps['frame'] = df_gps['actual_time']*24.97

    # df_gps = df_gps.round({'actual_time': 2, 'frame': 0})
    df_gps['frame'] = np.ceil(df_gps['frame'])
    df_gps['frame'] = df_gps['frame'].astype(int)

    # Create a df x gps
    df_gps_x_rois = pd.DataFrame(columns = [
        'gaze_timestamp',
        'actual_time',
        'frame',
        'true_x_scaled',
        'true_y_scaled',
        'confidence',
        'surface',
        # more columns to come: all roi's
    ])

    df_gps_x_rois['gaze_timestamp'] = df_gps['gaze_timestamp']
    df_gps_x_rois['actual_time'] = df_gps['actual_time']
    df_gps_x_rois['frame'] = df_gps['frame']
    df_gps_x_rois['true_x_scaled'] = df_gps['true_x_scaled']
    df_gps_x_rois['true_y_scaled'] = 1200 - df_gps['true_y_scaled']
    df_gps_x_rois['true_x_scaled_SRM'] = df_gps['true_x_scaled_SRM']
    df_gps_x_rois['true_y_scaled_SRM'] = 1200 - df_gps['true_y_scaled_SRM']
    df_gps_x_rois['confidence'] = df_gps['confidence']
    df_gps_x_rois['surface'] = df_gps['surface_no']

    new_cols = df_rois['Object ID'].unique().reshape(1, -1)[0]
    # df_gps_x_rois[new_cols] = np.zeros([len(new_cols), len(df_gps_x_rois)])

    zeros = np.zeros(shape=(len(df_gps_x_rois),len(new_cols)))
    df_gps_x_rois[new_cols] = pd.DataFrame(zeros, columns=new_cols)

    df_gps_x_rois.to_csv('../outputs/{}/df_gps_x_rois.csv'.format(participant_id))

    progress.print('We saved a preliminary df_gps_x_rois (with all hits to 0)')
    progress.update(task, total=(len(df_gps_x_rois)-1))
    progress.print('[bold yellow]Starting iterating all rows in df_gps_x_rois to identify hits')

    counter = 0
    for i, gp in df_gps_x_rois.iterrows():
        # Some nice progress output
        if(counter % 2000 == 0 or counter == 0):
            progress.print('[bold deep_pink4]Processed: {}/{}'.format(counter, len(df_gps_x_rois)))
        counter = counter + 1
        
        progress.advance(task)

        # Fetch ROIS on the same frame as the GP, 
        # if no rois are found, go to the next gaze position
        rois_to_consider = df_rois[df_rois['frame'] == gp['frame']]

        if(len(rois_to_consider) == 0):
            continue

        # We found rois to consider, let's do that now:
        for j, roi_to_consider in rois_to_consider.iterrows():
            
            is_hit = False

            x1 = roi_to_consider['x1']
            x2 = roi_to_consider['x2']
            y2 = 1200 - roi_to_consider['y2']
            y1 = 1200 - roi_to_consider['y1']
            angle = roi_to_consider['angle']

            x1, x2, y1, y2 = correct_aoi(x1, x2, y1, y2, angle)

            # Simple is "hit"
            # is_hit = ((x1 < gp['true_x_scaled'] < x2) and (y1 < gp['true_y_scaled'] < y2))
            is_hit = ((x1 < gp['true_x_scaled_SRM'] < x2) and (y1 < gp['true_y_scaled_SRM'] < y2))

            if(is_hit):
                # Change the zero to one if needed
                df_gps_x_rois.at[i, roi_to_consider['Object ID']] = 1

    progress.print('Done with iterating over all rows, now saving the file')
    progress.print('[bold green]Done! We saved df_gps_x_rois.csv with {} rows'.format(len(df_gps_x_rois)))
    df_gps_x_rois.to_csv('../outputs/{}/df_gps_x_rois.csv'.format(participant_id))

    progress.advance(task)
