import pandas as pd
from _preprocess import preprocess_gaze_positions
from remodnav.clf import EyegazeClassifier

# gp = pd.read_csv('gp_deel2.csv') # Load all gaze positions
# gp = preprocess_gaze_positions(gp) # Add velocities/accelerations column to gp

# gp.to_csv('temp.csv')
data = pd.read_csv('temp.csv')

clf = EyegazeClassifier()
prepared = clf.prepare(data) # TODO: prepare our data in a way that remodnav expects it

events = clf(prepared, classify_isp=True, sort_events=True)