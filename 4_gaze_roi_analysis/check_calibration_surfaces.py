import __constants
import pandas as pd
import sys, json

def check_calibration_surfaces(participant_id, calibration_file, progress, task):

    # Open surface gaze data
    calibration_surface_name = '../inputs/{}/gaze_positions_on_surface_ijksurface.csv'.format(participant_id)
    calibration_surface = pd.read_csv(calibration_surface_name)

    # Open the dummy surface
    dummy_surface_name = '../inputs/{}/gaze_positions_on_surface_dummysurface.csv'.format(participant_id)
    dummy_surface = pd.read_csv(dummy_surface_name)

    # Correct the timestamps in calibration_surface
    first_gaze_timestamp = dummy_surface.iloc[0]['gaze_timestamp']
    calibration_surface['gaze_timestamp'] = calibration_surface['gaze_timestamp'] - first_gaze_timestamp
    calibration_surface['frame'] = calibration_surface['gaze_timestamp'] * 25

    # Fetch expected frame numbers of the calibration surfaces
    input_file_name = '../calibration/{}'.format(calibration_file)

    # Fetch all entries and exits
    a_file = open(input_file_name, "r")
    calibration_frames = json.loads(a_file.read())

    i = 0
    for row in calibration_frames:
        # print(row['start'])
        # print(row['end'])

        # expect rows in calibration_surface to be found for which:
        # row['start'] <= calibration_surface['frame'] <= row['end']

        # rows_within_calibration = calibration_surface[(row['start'] <= calibration_surface['frame']) & row['end'] >= calibration_surface['frame']]

        # print('In calibration surface {} we found {} gaze position rows'.format(i, len(rows_within_calibration)))

        print(row['start'])
        print(row['end'])
        print('--')

        i = i + 1

    sys.exit()