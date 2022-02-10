import __constants
import pandas as pd
from utils__aois import prepare_aois_df
from utils__margin_calculator import correct_aoi
import numpy as np
from utils__general import show_error
import os.path

def identify_hits(participant_id, video_id, rois_file, progress, task):
    progress.print("[bold yellow]We are starting identifying hits")

    # Perpare ROI's
    df_rois = pd.read_csv('../rois/{}'.format(rois_file))
    df_rois = prepare_aois_df(df_rois)

    # Check if our input file exists
    input_file_name = '{}/{}/{}/gp.csv'.format(
        __constants.input_folder, participant_id, video_id)
    if not os.path.isfile(input_file_name):
        show_error('Input file for step 3 is not found. Run step 2 first.', progress)

    # Prepare merged surfaces with gaps
    df_gps = pd.read_csv(input_file_name)
    progress.print('found {} gaze position records'.format(len(df_gps)))

    # df_gps['frame'] = df_gps['t']*25 + 0.00001

    # # TODO: remove in january 2022
    # df_gps['frame'] = np.ceil(df_gps['frame'])
    # df_gps['frame'] = df_gps['frame'].astype(int)

    # Create a df x gps
    df_gps_x_rois = pd.DataFrame(columns = [
        't',
        'frame',
        'x',
        'y',
        # more columns to come: all roi's
    ])

    df_gps_x_rois['t'] = df_gps['t']
    df_gps_x_rois['frame'] = df_gps['frame']
    df_gps_x_rois['x'] = df_gps['x']
    df_gps_x_rois['y'] = df_gps['y']
    df_gps_x_rois['y_for_hit_calculation'] = 1200 - df_gps['y']

    new_cols = df_rois['Object ID'].unique().reshape(1, -1)[0]
    # df_gps_x_rois[new_cols] = np.zeros([len(new_cols), len(df_gps_x_rois)])

    zeros = np.zeros(shape=(len(df_gps_x_rois),len(new_cols)))
    df_gps_x_rois[new_cols] = pd.DataFrame(zeros, columns=new_cols)

    df_gps_x_rois.to_csv('../outputs/{}/{}/gp_x_aoi.csv'.format(participant_id, video_id))

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
        # rois frame and gp frame both starting at frame 0
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
            is_hit = ((x1 < gp['x'] < x2) and (y1 < gp['y_for_hit_calculation'] < y2))

            if(is_hit):
                # Change the zero to one if needed
                df_gps_x_rois.at[i, roi_to_consider['Object ID']] = 1

    progress.print('Done with iterating over all rows, now saving the file')
    progress.print('[bold green]Done! We saved df_gps_x_rois.csv with {} rows'.format(len(df_gps_x_rois)))
    df_gps_x_rois.to_csv('../outputs/{}/{}/gp_x_aoi.csv'.format(participant_id, video_id))

    progress.advance(task)
