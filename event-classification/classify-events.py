from typing import List
import __constants
import numpy as np
import pandas as pd

def preprocess_single_gaze_position(row) -> List[float]:
    # Previous vector
    a = np.array([row['previous_x'], row['previous_y'], __constants.d])

    # Current vector
    b = np.array([row['x'], row['y'], __constants.d])

    # By using dot product, calculate angle between the two vectors: cos 𝜙 = (a⋅b) / (|a||b|)
    cos_of_phi = np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
    phi = np.rad2deg(np.arccos(cos_of_phi))

    # Calculate the velocity (deg/s) and acceleration (deg/s^2) by dividing by constant sample rate
    velocity = phi / (1/__constants.sample_rate_ET)
    acceleration = phi / (1/__constants.sample_rate_ET)**2

    return [row['t'], row['x'], row['y'], row['frame'], velocity, acceleration]

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

gp = pd.read_csv('gp.csv') # Load all gaze positions
gp = preprocess_gaze_positions(gp) # Add velocities/accelerations column to gp
print(gp)

gp.to_csv('gp.temp.csv')