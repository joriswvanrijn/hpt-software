import pandas as pd
from _preprocess import preprocess_gaze_positions
from remodnav.clf import EyegazeClassifier
from _tools import overlay_video
import matplotlib.pyplot as plt
import sys

input_file = 'gp_deel2.csv'

'''1. Add velocities & accelerations'''
# gp = pd.read_csv(input_file) # Load all gaze positions
# gp = preprocess_gaze_positions(gp) # Add velocities/accelerations column to gp

# gp.to_csv('preproc_{}.csv'.format(input_file)) #checkpoint 1
gp = pd.read_csv('preproc_{}.csv'.format(input_file))

'''2. Compute events'''
clf = EyegazeClassifier()
prepared = clf.prepare(gp)
events = clf(prepared, classify_isp=True, sort_events=True)
events_pd = pd.DataFrame(events) 
# clf.show_gaze(prepared, prepared, events)
# plt.show()

# events_pd.to_csv('events_{}.csv'.format(input_file)) # checkpoint 2
# events_pd = pd.read_csv('events_{}.csv'.format(input_file))

'''3. Display stats'''
print(events_pd['label'].value_counts())

'''4. Overlay on video'''
# overlay_video(gp, events_pd, '../videos/Deel2.mp4', 'output.mp4')

'''5. Plot X/Y from gaze data and start of SACC from events'''
# Prepare events (add column for to plot)
# events_pd['plt_sacc'] = 0
# events_pd.loc[events_pd['label'] == 'SACC', 'plt_sacc'] = 100

# Create SACC column in gp, based on events_pd
# gp['plt_sacc'] = 0
# for index, row in events_pd.iterrows():
#     if(row['label'] == 'SACC'):
#         gp.loc[(gp['t'] > row['start_time']) & (gp['t'] < row['end_time']), 'plt_sacc'] = 1500

# # Plot the graph
# fig,ax = plt.subplots()
# ax.plot(gp['t'],gp['x'],label='x')
# ax.plot(gp['t'],gp['y'],label='y')
# ax.plot(gp['t'],gp['plt_sacc'],label='sacc')
# ax.set_xlabel("t")
# ax.set_ylabel("pos")
# ax.legend(loc='best')
# plt.show()