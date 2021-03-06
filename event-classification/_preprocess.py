import __constants
import pandas as pd
import numpy as np
from typing import List

def preprocess_single_gaze_position(row) -> List[float]:
    # Previous vector
    a = np.array([row['previous_x'], row['previous_y'], __constants.d])

    # Current vector
    b = np.array([row['x'], row['y'], __constants.d])

    # By using dot product, calculate angle between the two vectors: cos 𝜙 = (a⋅b) / (|a||b|)
    denominator = round(np.dot(a, b), 7)
    divisor = round(np.linalg.norm(a) * np.linalg.norm(b), 7)

    cos_of_phi = denominator / divisor
    phi = np.rad2deg(np.arccos(cos_of_phi))
    
    # print('n: ', np.dot(a, b))
    # print('d: ', (np.linalg.norm(a) * np.linalg.norm(b)))

    # Calculate the velocity (deg/s) and acceleration (deg/s^2) by dividing by constant sample rate
    velocity = phi / (1/__constants.sample_rate_ET)
    acceleration = phi / (1/__constants.sample_rate_ET)**2

    # this is the return we need for prepocessing our dat ain classify-events
    if('t' in row):
        return [row['t'], row['x'], row['y'], row['frame'], velocity, acceleration]
    
    # this is the return we need for _get_velocities in remodnav
    return velocity

def preprocess_gaze_positions(gp: pd.DataFrame) -> pd.DataFrame:
    '''Adds columns with velocities (deg/sec) and accelerations(deg/sec^2)
     to the dataframe based on gaze position (x, y)'''

    # Copy x and y, and shift it one up
    gp['previous_x'] = gp['x'].shift(1)
    gp['previous_y'] = gp['y'].shift(1)

    # Calculate velocity with lambda func
    gp = gp.apply(lambda row: 
        preprocess_single_gaze_position(row), 
        axis=1,
        result_type='expand'
    )

    # Rename the columns
    gp.columns = ['t', 'x', 'y', 'frame', 'velocity', 'acceleration']

    return gp
