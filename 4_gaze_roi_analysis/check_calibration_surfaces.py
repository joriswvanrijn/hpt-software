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

    # progress.print('[yellow]Calibration surface is {} rows long'.format(len(calibration_surface)))

    # for row in calibration_frames:
    #     progress.print('We are filtering all rows from our calibration surface between {} and {}'.format(row['start'], row['end']))
    #     calibration_surface = calibration_surface.drop(calibration_surface[(calibration_surface['frame'] < row['end']) & (calibration_surface['frame'] > row['start'])].index)

    # progress.print('[yellow]Calibration surface is {} rows long'.format(len(calibration_surface)))

    for i in range(len(calibration_frames) - 1):
        # per scene, we want to know how many calibration detections we find
        current = calibration_frames[i]
        next = calibration_frames[i+1]

        # find the amount of GP's between frame CURRENT.end and NEXT.start
        n = len(calibration_surface[(calibration_surface['frame'] > current['end']) & (calibration_surface['frame'] < next['start'])])

        progress.print('[purple]Found {} gps on ijksurface in scene {}'.format(n, i + 2))

    # TODO: make sure we save this output as well

    # TODO: remove this
    sys.exit()