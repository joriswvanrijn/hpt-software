from numpy import NaN
import __constants
import cv2, math
import pandas as pd

def compute_events_list(gp: pd.DataFrame, event_column: str) -> pd.DataFrame:
    events = pd.DataFrame(columns=['onset', 'offset', 'duration', 'label', 'start_x', 'start_y', 'end_x', 'end_y', 'amp', 'peak_vel', 'med_vel', 'avg_vel'])

    last_seen_label = gp.at[0, event_column]
    starting_index_of_last_seen_label = 0

    # Loop over all rows
    for index, row in gp.iterrows():

        if(index % 2000 == 0 or index == 0):
            print('Processed: {}/{}'.format(index, len(gp)))

        # New label encoutered
        if(not last_seen_label == row[event_column]):

            # Save label to events list
            events.loc[len(events), ['onset', 'offset', 'label']] = gp.at[starting_index_of_last_seen_label, 't'], gp.at[index, 't'], last_seen_label

            # Reset counters
            last_seen_label = row[event_column]
            starting_index_of_last_seen_label = index

    events['duration'] = events['offset'] - events['onset']

    return events

def overlay_video(gp: pd.DataFrame, events: pd.DataFrame, video_path: str, video_out_path: str):
    # open video
    cap = cv2.VideoCapture(video_path)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    # video to be saved
    out = cv2.VideoWriter(
        video_out_path,
        cv2.VideoWriter_fourcc(*'XVID'),
        cap.get(cv2.CAP_PROP_FPS),
        (int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)))
    )

    # convert coordinates (in GP the coordinates consider 0,0 as center)
    gp['x'] = gp['x'] + 2880 # x
    gp['y'] = abs(gp['y'] - 600) # y

    # loop over each frame
    current_frame = 0
    while(cap.isOpened()): 
        key = cv2.waitKey(1) & 0xff

        # quit on Q
        if key == ord('q'):
            break

        ret, frame = cap.read()

        # compute current time (video sample rate = 25Hz)
        current_time = current_frame / 25

        # plot the GP's (gp file sample rate = 240Hz)

        # TODO: make sure that the GP's are the same as in overlay_single_participant
        start_index_of_gp = int(round(current_time / (1/240)))
        end_index_of_gp = int(round((current_time + 1/25) / (1/240)))

        gps_to_display = gp[start_index_of_gp:end_index_of_gp]

        # reset x and y
        x = -1
        y = -1

        for index, gp_sample in gps_to_display.iterrows():
            if(not math.isnan(gp_sample['x']) and not math.isnan(gp_sample['y'])):
                x = int(gp_sample['x'])
                y = int(gp_sample['y'])
                cv2.circle(frame, (x, y), 20, (255, 255, 255), -1)  

        # select all events for which: onset <= current_time <= offset
        events_to_show = events[(events['onset'] <= current_time) & (current_time <= events['offset'])]

        nr_events_found = events_to_show.shape[0]
        print('found {} events'.format(nr_events_found))

        # if events are found, plot them on the screen
        if(nr_events_found > 0 and x > 0 and y > 0):
            label = events_to_show.iloc[0, events_to_show.columns.get_loc('label')]

            color = (220, 117, 0)

            if(label == 'SACC'):
                color = (72, 206, 43)
            elif(label == 'PURS'):
                color = (5, 164, 255)
            elif(label == 'LPSO'):
                color =  (242, 241, 94)
            elif(label == 'GAP'):
                color =  (40, 0, 221)

            cv2.rectangle(frame, (x + 20, y + 20), (x + 170, y + 100), color, -1, 1)
            cv2.putText(frame, label, (x + 40, y + 70), cv2.FONT_HERSHEY_SIMPLEX, 
                1.5, (255, 255, 255), 4, cv2.LINE_AA);

        # display frame
        cv2.imshow('Frame', frame) 
        cv2.moveWindow('Frame', 20, 20)

        # write frame
        print('saving frame {}/{}'.format(current_frame, total_frames))
        out.write(frame)
        
        # increase frame number
        current_frame = current_frame + 1


    # video opslaan
    cap.release()
    out.release()
