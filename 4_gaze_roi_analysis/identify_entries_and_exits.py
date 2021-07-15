import __constants
import pandas as pd
from utils__aois import prepare_aios_df
from utils__general import show_error
import os.path
import json

def identify_entries_and_exits(participant_id, rois_file, progress, task):
    progress.print("[bold yellow]We are starting identifying entries and exits")

    input_file_name = '../outputs/{}/df_gps_x_rois.csv'.format(participant_id)
    if not os.path.isfile(input_file_name):
        show_error('Input file for step 4 is not found. Run step 3 first.', progress)

    # Perpare ROI's
    df_rois = pd.read_csv('../rois/{}'.format(rois_file))
    df_rois = prepare_aios_df(df_rois)

    entries_and_exits = {}
    consecutive_0_treshold_counter = 0
    consecutive_0_treshold_first_placeholder = None

    rois = df_rois['Object ID'].unique()

    for roi in rois:
        entries_and_exits[roi] = []

    # Loop over all gps(x)rois
    df_gps_x_rois = pd.read_csv(input_file_name)

    progress.update(task, total=(len(df_gps_x_rois)-1))
    progress.print('[bold yellow]Starting iterating all rows in df_gps_x_rois to identify entries and exits')

    counter = 0
    for i, hit_row in df_gps_x_rois.iterrows():
        # Some nice progress output
        if(counter % 2000 == 0 or counter == 0):
            progress.print('[bold deep_pink4]Processed: {}/{}'.format(counter, len(df_gps_x_rois)))
        counter = counter + 1

        progress.advance(task)

        # Loop over all rois to check if we have seen a one

        # for roi in rois:

        #     if(hit_row[roi] == 1 and len(entries_and_exits[roi]) % 2 == 0):
        #         # We're looping and finding a 1 AND the previous found mark was an exit
        #         # so mark this moment as an entry
        #         entries_and_exits[roi].append(hit_row['actual_time'])

        #     if(hit_row[roi] == 0 and len(entries_and_exits[roi]) % 2 != 0):
        #         # If we are finding a 0 and we may register an exit, do it
        #         entries_and_exits[roi].append(hit_row['actual_time'])

        for roi in rois:

            if(hit_row[roi] == 1 and len(entries_and_exits[roi]) % 2 == 0):
                # We're looping and finding a 1 AND the previous found mark was an exit
                # so mark this moment as an entry
                entries_and_exits[roi].append(hit_row['actual_time'])

            # Everytime we find a 1, reset our counters and placeholder
            if(hit_row[roi] == 1):
                consecutive_0_treshold_counter = 0
                consecutive_0_treshold_first_placeholder = None

            if(hit_row[roi] == 0 and len(entries_and_exits[roi]) % 2 != 0):
                # If we have no "first 0", save it
                if(consecutive_0_treshold_first_placeholder == None):
                    consecutive_0_treshold_first_placeholder = hit_row['actual_time']
                    
                # We're looping and finding a 0 AND the previous found mark was an entry
                # so mark this moment as an exit
                if(consecutive_0_treshold_counter >= __constants.consecutive_0_treshold):
                    entries_and_exits[roi].append(consecutive_0_treshold_first_placeholder)
                    consecutive_0_treshold_counter = 0
                    consecutive_0_treshold_first_placeholder = None
                else:
                    consecutive_0_treshold_counter = consecutive_0_treshold_counter + 1
    
    progress.advance(task)

    entries_exits_file = '../outputs/{}/entries_exits.json'.format(participant_id)

    file_handle = open(entries_exits_file, "w")
    json.dump(entries_and_exits, file_handle)
    file_handle.close()

    progress.print('[bold green]Done! We found and saved all entries and exits')
    # progress.print(entries_and_exits)