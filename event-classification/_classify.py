import __constants
import pandas as pd
import numpy as np

def classify_gaps(gp: pd.DataFrame) -> pd.DataFrame:
    gp['event'] = np.NaN

    # Classify all spikes as GAP (unrealistic high velocities or accelerations)
    gp.loc[gp['velocity'] > __constants.max_velocity_treshold, 'event'] = 'GAP'
    gp.loc[gp['acceleration'] > __constants.max_acceleration_treshold, 'event'] = 'GAP'

    # Get all gaps and classify 8ms (i.e. 2 samples) before and after these gaps as GAP
    gap_gp = gp[gp['event'] == 'GAP']
    for index, row in gap_gp.iterrows():
        gp.at[index-2:index+2, 'event'] = 'GAP'

    # Classify all missing data as GAP
    gp.loc[gp['velocity'].isna(), 'event'] = 'GAP'
    gp.loc[gp['acceleration'].isna(), 'event'] = 'GAP'

    return gp

def classify_events_ivtfix(gp: pd.DataFrame) -> pd.DataFrame:
    gp['event_ivtfix'] = gp['event']

    # Classify fixations
    gp.loc[
        (gp['velocity'] < 30) & (gp['event_ivtfix'].isna()),
        'event_ivtfix'
    ] = 'FIX'
    
    # Classify saccades (all others)
    gp.loc[
        gp['event_ivtfix'].isna(),
        'event_ivtfix'
    ] = 'SACC'

    return gp
