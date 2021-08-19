import __constants
import numpy as np
from scipy.interpolate import PchipInterpolator
import pandas as pd
import numpy.linalg as LA
import sys
import matplotlib.pyplot as plt
from numpy import pi, cos, sin, arctan
import math

def detect_saccades(participant_id, video_id):
    engbert_lambda = 5

    print("[bold yellow]We are starting identifying saccades")

    # Read the csv
    input_file_name = '../outputs/{}/{}/df_gps_x_rois.csv'.format(participant_id, video_id)
    samples = pd.read_csv(input_file_name)

    # Interpolate the data 
    # true_x_scaled_SRM, true_y_scaled_SRM
    fs = 240
    interpgaze = interpolate_gaze(samples, participant_id, video_id, fs=fs)

    # calculate x and y in terms of rad
    interpgaze = gaze_coordinates_to_rad(samples)

    # apply the saccade detection algorithm     
    saccades = apply_engbert_mergenthaler(xy_data=interpgaze[['x_rad', 'y_rad']], is_blink=interpgaze['is_blink'], vel_data=None, sample_rate=fs, l=engbert_lambda)

    # convert samples of data back to sample time
    for fn in ['raw_start_time', 'raw_end_time', 'expanded_start_time', 'expanded_end_time']:
        saccades[fn] = np.array(interpgaze.actual_time.iloc[np.array(saccades[fn])])

    # print(saccades.head(10))

    # Save saccades to csv
    output_file_name = '../outputs/{}/{}/saccades.csv'.format(participant_id, video_id)
    saccades.to_csv(output_file_name)

    # return saccades

def interpolate_gaze(samples, participant_id, video_id, fs=None):
    print("[bold yellow]We are starting to interpolate gaze data")

    samples['true_x_scaled_SRM'].fillna(0, inplace=True)
    samples['true_y_scaled_SRM'].fillna(0, inplace=True)

    # find the time range
    fromT = samples.actual_time.iloc[0]  # find the first sample
    toT = samples.actual_time.iloc[-1]  # find the last sample

    # we find the new index
    timeIX = np.linspace(int(np.floor(fromT)), int(np.ceil(toT)), int(np.ceil(toT - fromT) * fs + 1))

    def interp(x, y):
        f = PchipInterpolator(x, y, extrapolate=True)
        return f(timeIX)

    gazeInt = pd.DataFrame()
    gazeInt.loc[:, 'actual_time'] = timeIX

    gazeInt.loc[:, 'true_x_scaled_SRM'] = interp(samples.actual_time, samples.true_x_scaled_SRM)
    gazeInt.loc[:, 'true_y_scaled_SRM'] = interp(samples.actual_time, samples.true_y_scaled_SRM)
    gazeInt.loc[:, 'is_blink'] = interp(samples.actual_time, samples.is_blink)

    output_file_name = '../outputs/{}/{}/interpolated_gazedata.csv'.format(participant_id, video_id)
    gazeInt.to_csv(output_file_name)

    # actual_time, true_x_scaled_SRM, true_y_scaled_SRM
    # samples x
    # gazeInt

    # plt.plot(samples.actual_time, samples.true_x_scaled_SRM, 'r')
    # plt.plot(gazeInt.actual_time, gazeInt.true_x_scaled_SRM, 'g')
    # plt.show()

    # plt.plot(samples.actual_time, samples.true_y_scaled_SRM, 'r')
    # plt.plot(gazeInt.actual_time, gazeInt.true_y_scaled_SRM, 'g')
    # plt.show()

    return gazeInt


    print('foobar')
    # TODO:

def apply_engbert_mergenthaler(xy_data=None, is_blink=None, vel_data=None, l=5, sample_rate=None,
                               minimum_saccade_duration=0.0075):
    """Uses the engbert & mergenthaler algorithm (PNAS 2006) to detect saccades.
    
    This function expects a sequence (N x 2) of xy gaze position or velocity data. 
    
    Arguments:
        xy_data (numpy.ndarray, optional): a sequence (N x 2) of xy gaze (float/integer) positions. Defaults to None
        vel_data (numpy.ndarray, optional): a sequence (N x 2) of velocity data (float/integer). Defaults to None.
        l (float, optional):determines the threshold. Defaults to 5 median-based standard deviations from the median
        sample_rate (float, optional) - the rate at which eye movements were measured per second). Defaults to 1000.0
        minimum_saccade_duration (float, optional) - the minimum duration for something to be considered a saccade). Defaults to 0.0075
    
    Returns:
        list of dictionaries, which each correspond to a saccade.
        
        The dictionary contains the following items:
            
    Raises:
        ValueError: If neither xy_data and vel_data were passed to the function.
    
    """

    print('Detecting saccades ...')

    # If xy_data and vel_data are both None, function can't continue
    if xy_data is None and vel_data is None:
        raise ValueError("Supply either xy_data or vel_data")

        # If xy_data is given, process it
    if not xy_data is None:
        xy_data = np.array(xy_data)
    if is_blink is None:
        raise ('error you have to give me blink data!')
    # Calculate velocity data if it has not been given to function
    if vel_data is None:
        # # Check for shape of xy_data. If x and y are ordered in columns, transpose array.
        # # Should be 2 x N array to use np.diff namely (not Nx2)
        # rows, cols = xy_data.shape
        # if rows == 2:
        #     vel_data = np.diff(xy_data)
        # if cols == 2:
        #     vel_data = np.diff(xy_data.T)
        vel_data = np.zeros(xy_data.shape)
        vel_data[1:] = np.diff(xy_data, axis=0)
    else:
        vel_data = np.array(vel_data)

    inspect_vel = pd.DataFrame(vel_data)
    inspect_vel.describe()

    # median-based standard deviation, for x and y separately
    med = np.nanmedian(vel_data, axis=0)

    std = np.nanmean(np.array(np.sqrt((vel_data - med) ** 2)), axis=0)
    scaled_vel_data = vel_data / std  # scale by the standard deviation

    print('Std of velocity data %s', np.round(std, 4))
    # normalize and to acceleration and its sign
    if (float(np.__version__.split('.')[1]) == 1.0) and (float(np.__version__.split('.')[1]) > 6):
        normed_scaled_vel_data = LA.norm(scaled_vel_data, axis=1)
        normed_vel_data = LA.norm(vel_data, axis=1)
    else:
        normed_scaled_vel_data = np.array([LA.norm(svd) for svd in np.array(scaled_vel_data)])
        normed_vel_data = np.array([LA.norm(vd) for vd in np.array(vel_data)])

    normed_acc_data = np.r_[0, np.diff(normed_scaled_vel_data)]
    signed_acc_data = np.sign(normed_acc_data)

    # when are we above the threshold, and when were the crossings
    # Deleted nans due to spyder bug https://github.com/numpy/numpy/issues/11029
    # This is just aesthetics so we do not get a runtime warning
    normed_scaled_vel_data[np.isnan(normed_scaled_vel_data)] = -1
    print('using a threshold of %.2f lambda' % (l))
    over_threshold = (normed_scaled_vel_data > l)
    print('Mean overthreshold values: %s', np.round(over_threshold.mean(), 4))
    # integers instead of bools preserve the sign of threshold transgression
    over_threshold_int = np.array(over_threshold, dtype=np.int16)

    # crossings come in pairs
    threshold_crossings_int = np.concatenate([[0], np.diff(over_threshold_int)])
    threshold_crossing_indices = np.arange(threshold_crossings_int.shape[0])[threshold_crossings_int != 0]

    valid_threshold_crossing_indices = []

    # if no saccades were found, then we'll just go on and record an empty saccade
    if threshold_crossing_indices.shape[0] > 1:
        # the first saccade cannot already have started now
        if threshold_crossings_int[threshold_crossing_indices[0]] == -1:
            threshold_crossings_int[threshold_crossing_indices[0]] = 0
            threshold_crossing_indices = threshold_crossing_indices[1:]

        # the last saccade cannot be in flight at the end of this data
        if threshold_crossings_int[threshold_crossing_indices[-1]] == 1:
            threshold_crossings_int[threshold_crossing_indices[-1]] = 0
            threshold_crossing_indices = threshold_crossing_indices[:-1]

        # if threshold_crossing_indices.shape == 0:
        # break
        # check the durations of the saccades
        threshold_crossing_indices_2x2 = threshold_crossing_indices.reshape((-1, 2))
        raw_saccade_durations = np.diff(threshold_crossing_indices_2x2, axis=1).squeeze()

        # and check whether these saccades were also blinks...
        blinks_during_saccades = np.ones(threshold_crossing_indices_2x2.shape[0], dtype=bool)
        for i in range(blinks_during_saccades.shape[0]):
            if np.any(is_blink[threshold_crossing_indices_2x2[i, 0]:threshold_crossing_indices_2x2[i, 1]]):
                blinks_during_saccades[i] = False

        # and are they too close to the end of the interval?
        right_times = threshold_crossing_indices_2x2[:, 1] < xy_data.shape[0] - 30

        valid_saccades_bool = ((raw_saccade_durations / float(
            sample_rate) > minimum_saccade_duration) * blinks_during_saccades) * right_times
        if type(valid_saccades_bool) != np.ndarray:
            valid_threshold_crossing_indices = threshold_crossing_indices_2x2
        else:
            valid_threshold_crossing_indices = threshold_crossing_indices_2x2[valid_saccades_bool]

        # print threshold_crossing_indices_2x2, valid_threshold_crossing_indices, blinks_during_saccades,
        # ((raw_saccade_durations / sample_rate) > minimum_saccade_duration), right_times, valid_saccades_bool print
        # raw_saccade_durations, sample_rate, minimum_saccade_duration
    print('Number of saccades detected: %s', valid_threshold_crossing_indices.shape)

    saccades = []
    for i, cis in enumerate(valid_threshold_crossing_indices):
        if i % 1000 == 0:
            print(i)
        # find the real start and end of the saccade by looking at when the acceleleration reverses sign before the
        # start and after the end of the saccade: sometimes the saccade has already started?
        expanded_saccade_start = np.arange(cis[0])[np.r_[0, np.diff(signed_acc_data[:cis[0]] != 1)] != 0]
        if expanded_saccade_start.shape[0] > 0:
            expanded_saccade_start = expanded_saccade_start[-1]
        else:
            expanded_saccade_start = 0

        expanded_saccade_end = np.arange(cis[1], np.min([cis[1] + 50, xy_data.shape[0]]))[
            np.r_[0, np.diff(signed_acc_data[cis[1]:np.min([cis[1] + 50, xy_data.shape[0]])] != -1)] != 0]
        # sometimes the deceleration continues crazily, we'll just have to cut it off then. 
        if expanded_saccade_end.shape[0] > 0:
            expanded_saccade_end = expanded_saccade_end[0]
        else:
            expanded_saccade_end = np.min([cis[1] + 50, xy_data.shape[0]])

        try:
            this_saccade = {
                # expanded means: taking more sampls as looking at accelartion values as well    
                'expanded_start_time': expanded_saccade_start,
                'expanded_end_time': expanded_saccade_end,
                'expanded_duration': (expanded_saccade_end - expanded_saccade_start) * 1. / sample_rate,
                'expanded_start_gx': xy_data[expanded_saccade_start][0],
                'expanded_start_gy': xy_data[expanded_saccade_start][1],
                'expanded_end_gx': xy_data[expanded_saccade_end][0],
                'expanded_end_gy': xy_data[expanded_saccade_end][1],
                'expanded_amplitude': np.sum(normed_vel_data[expanded_saccade_start:expanded_saccade_end]),
                'expanded_peak_velocity': np.max(
                    normed_vel_data[expanded_saccade_start:expanded_saccade_end]) * sample_rate,

                # only velocity based
                'raw_start_time': cis[0],
                'raw_end_time': cis[1],
                'raw_duration': (cis[1] - cis[0]) * 1. / sample_rate,
                'raw_start_gx': xy_data[cis[1]][0],
                'raw_start_gy': xy_data[cis[1]][1],
                'raw_end_gx': xy_data[cis[0]][0],
                'raw_end_gy': xy_data[cis[0]][1],
                # no need to calculate the raw_amplitude here as we will calculate the SPHERICAL amplitude later
                # 'raw_amplitude': np.sum(normed_vel_data[cis[0]:cis[1]]),
                'raw_peak_velocity': np.max(normed_vel_data[cis[0]:cis[1]]) * sample_rate,

            }
            saccades.append(this_saccade)
        except IndexError:
            pass

    # if this fucker was empty
    if len(valid_threshold_crossing_indices) == 0:
        this_saccade = {
            'expanded_start_time': 0,
            'expanded_end_time': 0,
            'expanded_duration': 0.0,
            'expanded_start_gx': 0.0,
            'expanded_end_gx': 0.0,
            'expanded_start_gy': 0.0,
            'expanded_end_gy': 0.0,
            'expanded_amplitude': 0.0,
            'expanded_peak_velocity': 0.0,

            'raw_start_time': 0,
            'raw_end_time': 0,
            'raw_duration': 0.0,
            'raw_start_gx': 0.0,
            'raw_end_gx': 0.0,
            'raw_start_gy': 0.0,
            'raw_end_gy': 0.0,
            'raw_amplitude': 0.0,
            'raw_peak_velocity': 0.0,
        }
        saccades.append(this_saccade)

    # shell()

    # convert into pandas df
    saccade_df = pd.DataFrame(saccades)

    # calculate the spherical angle
    saccade_df['raw_amplitude'] = saccade_df.apply(
        lambda localrow: calc_3d_angle_points(localrow.raw_start_gx, localrow.raw_start_gy, localrow.raw_end_gx,
                                                      localrow.raw_end_gy), axis=1)

    print('Done... detecting saccades')

    return saccade_df

def calc_3d_angle_points(x_0, y_0, x_1, y_1):
    # calculate the spherical angle between 2 points We add pi/2 so that (0°,0°,1), and (0°,90°,1) have a distance of
    # 90° instead of 0. (we take the "y" axis as the "0°,0°")
    #
    vec1 = sph2cart(x_0 / 360 * 2 * pi + pi / 2, y_0 / 360 * 2 * pi + pi / 2)
    vec2 = sph2cart(x_1 / 360 * 2 * pi + pi / 2, y_1 / 360 * 2 * pi + pi / 2)

    # pupillabs : precision = np.sqrt(np.mean(np.rad2deg(np.arccos(succesive_distances.clip(-1., 1.))) ** 2))
    cosdistance = np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))
    angle = np.arccos(np.clip(cosdistance, -1., 1.))
    angle = angle * 360 / (2 * pi)  # radian to degree

    return angle

def sph2cart(theta_sph, phi_sph, rho_sph=1):
    xyz_sph = np.asarray([rho_sph * sin(theta_sph) * cos(phi_sph),
                          rho_sph * sin(theta_sph) * sin(phi_sph),
                          rho_sph * cos(theta_sph)])

    return xyz_sph

def gaze_coordinates_to_rad(samples):
    samples['x_rad'] = arctan(samples['true_x_scaled_SRM'] / __constants.distance_to_screen_px)
    samples['y_rad'] = arctan(samples['true_y_scaled_SRM'] / __constants.distance_to_screen_px)

    output_file_name = '../outputs/{}/temporary.csv'.format('inputRVR')
    samples.to_csv(output_file_name)

    # plt.plot(samples.actual_time, samples.true_x_scaled_SRM, 'r')
    # plt.plot(samples.actual_time, samples.x_rad * 1000, 'g')
    # plt.show()
    
    return samples

detect_saccades('inputRVR', 'validatietaak')