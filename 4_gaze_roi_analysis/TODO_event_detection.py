import pandas as pd
import numpy as np
import math
import matplotlib

def dotproduct(v1, v2):
  return sum((a*b) for a, b in zip(v1, v2))

def length(v):
  return math.sqrt(dotproduct(v, v))

def angle(v1, v2):
  return math.acos(dotproduct(v1, v2) / (length(v1) * length(v2)))

df_gps = pd.read_csv('../4_gaze_positions_preperation/merged_surfaces.csv')
print('found {} gaze position records'.format(len(df_gps)))

minimal_confidence = 0.01

df_gps['actual_time'] = df_gps['gaze_timestamp']-abs(df_gps.loc[0, 'gaze_timestamp'])
df_gps['frame'] = df_gps['actual_time']*24.97

# df_gps = df_gps.round({'actual_time': 2, 'frame': 0})
df_gps['frame'] = df_gps['frame'].astype(int)

df_gps = df_gps[df_gps['confidence'] > minimal_confidence]

print(df_gps.head())
df_gps.to_csv('df_gps.csv')

# Some variables
distance_to_screen = 65.06 # in cm
ppi = 94.34 # pixels per inch
ppc = ppi/2.54 # 37,141732283
z = d = distance_to_screen_px = distance_to_screen * ppc

# velocity: degrees/s
# velocity: px/s
# degrees -> obv afstand (in px)
# sec --> obv |timestamp(t) - timestamp(t + 1)|

df_gps['true_x_scaled_prev'] = df_gps['true_x_scaled']
df_gps['true_x_scaled_prev'] = df_gps['true_x_scaled_prev'].shift(1)

df_gps['true_y_scaled_prev'] = df_gps['true_y_scaled']
df_gps['true_y_scaled_prev'] = df_gps['true_y_scaled_prev'].shift(1)

# df_gps['euclidian_distance_with_prev'] = (
#     (df_gps['true_x_scaled'] - df_gps['true_x_scaled_prev'])**2 + 
#     (df_gps['true_y_scaled'] - df_gps['true_y_scaled_prev'])**2
# )**(1/2)

df_gps['actual_time_prev'] = df_gps['actual_time']
df_gps['actual_time_prev'] = df_gps['actual_time_prev'].shift(1)

# df_gps['velocity'] = df_gps['euclidian_distance_with_prev'] / (df_gps['actual_time'] - df_gps['actual_time_prev'])

# df_gps['angle'] = math.degrees(angle(
#     np.array([df_gps['true_x_scaled'], df_gps['true_y_scaled'], z]), # vector 1
#     np.array([df_gps['true_x_scaled_prev'], df_gps['true_y_scaled_prev'], z]), # vector 2
# ))

# def dotproduct(v1, v2):
#   return sum((a*b) for a, b in zip(v1, v2))

# def length(v):
#   return math.sqrt(dotproduct(v, v))

# def angle(v1, v2):
#   return math.acos(dotproduct(v1, v2) / (length(v1) * length(v2)))

df_gps['dot_product'] = df_gps['true_x_scaled'] * df_gps['true_x_scaled_prev'] + df_gps['true_y_scaled'] * df_gps['true_y_scaled_prev'] + z*z
df_gps['length_v1'] = (df_gps['true_x_scaled_prev']**2 + df_gps['true_y_scaled_prev']**2 + z**2)**(1/2)
df_gps['length_v2'] = (df_gps['true_x_scaled']**2 + df_gps['true_y_scaled']**2 + z**2)**(1/2)
df_gps['angle'] = np.degrees(np.arccos(df_gps['dot_product'] / (df_gps['length_v1'] * df_gps['length_v2'])))

df_gps['velocity'] = df_gps['angle'] / (df_gps['actual_time'] - df_gps['actual_time_prev'])

df_gps.head()

# x-> actual time, y -> velocity

df_gps = df_gps.iloc[1:]

# df_gps[(df_gps['velocity'] < 700) & (10 < df_gps['actual_time'] < 15)].plot(x='actual_time', y='velocity', kind='line', figsize=(40, 5))
df_gps.query('velocity < 700 & 10 < actual_time < 20').plot(x='actual_time', y='velocity', kind='line', figsize=(40, 5))
