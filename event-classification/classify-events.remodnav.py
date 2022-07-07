import pandas as pd
from _preprocess import preprocess_gaze_positions
from remodnav.clf import EyegazeClassifier
from _tools import overlay_video

input_file = 'gp_deel2.csv'

'''1. Add velocities & accelerations'''
gp = pd.read_csv(input_file) # Load all gaze positions
gp = preprocess_gaze_positions(gp) # Add velocities/accelerations column to gp

gp.to_csv('preproc_{}.csv'.format(input_file)) #checkpoint 1
gp = pd.read_csv('preproc_{}.csv'.format(input_file))

'''2. Compute events'''
clf = EyegazeClassifier()
prepared = clf.prepare(gp)
events = clf(prepared, classify_isp=True, sort_events=True)
events_pd = pd.DataFrame(events) 

events_pd.to_csv('events_{}.csv'.format(input_file)) # checkpoint 2
events_pd = pd.read_csv('events_{}.csv'.format(input_file))

'''3. Overlay on video'''
overlay_video(gp, events_pd, '../videos/Deel2.mp4', 'output.mp4')