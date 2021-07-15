import argparse
import pandas as pd
import cv2, os, sys
import time, math

sys.path.append('../4_gaze_rois_analysis')
import __constants
from utisl__aois import prepare_aios_df
from utisl__margin_calculator import correct_aoi

# parse the arguments used to call this script
parser = argparse.ArgumentParser()
parser.add_argument('--video', help='path of video file', type=str)
parser.add_argument('--data', help='path of the ROI csv file', type=str)
parser.add_argument('--gazedata', help='path of the GAZE POSITION csv file', type=str)
parser.add_argument('--offset', help='offset of the frames in the data set', type=int, default=0)
parser.add_argument('--start_frame', help='start playing at frame', type=int, default=0)

args = parser.parse_args()
video_path = args.video
data_path = args.data # ROI data
gaze_data_path = args.gazedata # Gaze data
offset = args.offset
start_frame = args.start_frame - 1

def ResizeWithAspectRatio(image, width=None, height=None, inter=cv2.INTER_AREA):
    dim = None
    (h, w) = image.shape[:2]

    if width is None and height is None:
        return image
    if width is None:
        r = height / float(h)
        dim = (int(w * r), height)
    else:
        r = width / float(w)
        dim = (width, int(h * r))

    return cv2.resize(image, dim, interpolation=inter)

# Read data file
df = pd.read_csv(data_path, header=0)
df_gp = pd.read_csv(gaze_data_path, header=0)

# Prepare data
df = prepare_aios_df(df)

df_gp['actual_time'] = df_gp['gaze_timestamp']-abs(df_gp.loc[0, 'gaze_timestamp'])
# df_gp['true_y_scaled'] = 1200-df_gp['true_y_scaled'] # Inverse the y coordinates 
df_gp['frame'] = df_gp['actual_time']*24.97
df_gp['frame'] = df_gp['frame'].astype(int)

# Read video
cap = cv2.VideoCapture(video_path)
cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

# Write video
out = cv2.VideoWriter(
        'video_with_labels.mp4',
        cv2.VideoWriter_fourcc(*'XVID'),
        cap.get(cv2.CAP_PROP_FPS),
        (int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)))
    )

if (cap.isOpened()== False):  
    print("Error opening video file") 
else:
    print("Press Q to quit, P to pause\n") 
    print("Red: must be seen, Blue: may be seen") 

paused = False

# Read until video is completed 
frame_nr = start_frame

# Capture frame-by-frame 
while(cap.isOpened()): 
    key = cv2.waitKey(1) & 0xff

    # quit on Q
    if key == ord('q'):
        break

    # pause on P
    if key == ord('p'):
        paused = not paused

    if paused == False:
        ret, frame = cap.read()

        if ret == True:
            frame_nr = frame_nr + 1
            overlays = df[df['Frame'] == (frame_nr - offset)]
            
            # HIERZO: inladen GP voor tijd (ongeveer) rond hier
            actual_time  = frame_nr / 24.97
            # print('considering frame {} -> actual time: {}'.format(frame_nr, actual_time))

            marge = 0.01
            # gaze_position_overlays = df_gp[(df_gp['actual_time'] < actual_time + marge) & (df_gp['actual_time'] > actual_time - marge)]
            gaze_position_overlays = df_gp[df_gp['frame'] == frame_nr]
            print('found {} gaze positions around frame {}'.format(len(gaze_position_overlays), frame_nr))

            for index, gaze_position in gaze_position_overlays.iterrows():
                if not math.isnan(gaze_position['true_x_scaled_SRM']) and not math.isnan(gaze_position['true_y_scaled_SRM']):
                    x = gaze_position['true_x_scaled'] + __constants.total_surface_width/2
                    y = 1200 - (gaze_position['true_y_scaled'] + __constants.total_surface_height/2)

                    # print('x: {}, y: {}'.format(x,y))

                    cv2.circle(frame, (int(x), int(y)), 20, (161, 254, 141), -1)

            # print('considering frame {}'.format(frame_nr))
            # print('found {} overlay(s) in data frame'.format(len(overlays)))

            # Draw frame nr on frame
            cv2.rectangle(frame, (0, 0), (400, 80), (255, 255, 255), -1, 1)
            cv2.putText(frame, "Frame: {}".format(frame_nr), (0, 50), 
                            cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 0), 2, cv2.LINE_AA);

            # Draw overlays on frame
            for index, overlay in overlays.iterrows():

                # Since we have "prepared" the aois into the new coordinates
                # calculate this back
                y1 = overlay['y1'] + __constants.total_surface_height/2
                y2 = overlay['y2'] + __constants.total_surface_height/2
                x1 = overlay['x1'] + __constants.total_surface_width/2
                x2 = overlay['x2'] + __constants.total_surface_width/2
                y1 = 1200-y1 # Inverse the y coordinates to match with pupil labs data
                y2 = 1200-y2 

                if 'type' in overlay and overlay['type'] == 'may':
                    color = (254, 141, 141)
                    color2 = (254, 10, 10)
                else:
                    color = (141, 141, 254)
                    color2 = (10, 10, 254)

                # Original coordinates
                p1 = (int(x1), int(y1))
                p2 = (int(x2), int(y2))

                cv2.rectangle(frame, (p1[0], p1[1] - 40), (p2[0], p1[1]), color, -1, 1)
                cv2.rectangle(frame, p1, p2, color, 2, 1)

                cv2.putText(frame, "{}".format(overlay['Object ID']), (p1[0], p1[1] - 20), 
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA);

                # Corrected points
                new_x1, new_x2, new_y1, new_y2 = correct_aoi(x1, x2, y1, y2, overlay['angle'])

                new_p1 = (int(new_x1), int(new_y1))
                new_p2 = (int(new_x2), int(new_y2))

                cv2.rectangle(frame, new_p1, new_p2, color2, 2, 1)

            # Display the resulting frame
            frame = ResizeWithAspectRatio(frame, width=2500) 
            cv2.imshow('Frame', frame) 
            cv2.moveWindow('Frame', 20, 20)

            # Writing the resulting frame
            # print('saving frame {}/{}'.format(frame_nr, total_frames))
            # out.write(frame)
    
        # Break the loop 
        else:  
            break

cap.release()
out.release()