import pandas as pd
from _classify import classify_gaps, classify_events_ivtfix
from _preprocess import preprocess_gaze_positions
from _tools import overlay_video, compute_events_list

# gp = pd.read_csv('gp_deel2.csv') # Load all gaze positions
# gp = preprocess_gaze_positions(gp) # Add velocities/accelerations column to gp
# gp = classify_gaps(gp) # Classify gap events
# gp = classify_events_ivtfix(gp) # Classify events
# gp.to_csv('gp_deel2.temp.csv')
# gp = pd.read_csv('gp_deel2.temp.csv')

# events = compute_events_list(gp, 'event_ivtfix')
# events.to_csv('events.csv')

gp = pd.read_csv('gp_deel2.temp.csv')
events = pd.read_csv('events.csv')

overlay_video(gp, events, '../videos/val.mp4', 'overlayed.mp4')