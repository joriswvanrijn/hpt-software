# ROI selection/detection

The goal of this part of the HPT tooling is to translate humanly-identified MUST/MAY be seen hazards to data files. This can be done semi-automatically or manually. Both methods can be used intertwined, after which we can comnine the data files. We can check the data files by overlaying the csv files over a video.

1. Method 1: Tracking objects semi-automatically
1. Method 2: Selecting ROI's manually
1. Combining csv files from the two methods above
1. Overlaying a data file over a video

## Method 1: Tracking objects semi-automatically

```bash
python3 object_tracking.py --name "../videos/vid.mp4" --label="stoplicht" --start_frame=70
```

**Usage:**

1. Run the command above, replacing `vid.mp4` with the path to your video
1. The video will open a preview screen
1. If you want to select an object to track from the first frame, draw a box on the video
1. If not: hint `[enter]` to play the video, hit `[s]` when you want to select an object
1. The video starts playing and shows the tracked object. In this state, the results are directly saved to your output csv
1. When you're done, stop the script by hitting `[q]`

> Note: it is possible to select multiple ROI's in one video! The script will automatically use all given ROI's.

## Method 2: Selection ROI

```bash
python3 roi_selection.py --name="../videos/vid.mp4" --label="stoplicht" --start-frame=100
```

**Usage:**

1. Run the command above, replacing `videos/vid.mp4` with the path to your video
1. The video will open a preview screen
1. If you want to select a ROI from the first frame
1. If not: hint `[enter]` to play the video, hit `[s]` when you want to select a ROI
1. The video starts playing **without** showing the ROI. when you want to select a new ROI, hit `[s]`
1. When you're done, stop the script by hitting `[q]`
1. The script will print the selected bounding boxes to the console and calculate the coordinates of the ROI in between
1. The script will show you the computed ROI's by showing the video again and save it to the output file.

## Combining csv files

```bash
python3 concat_files.py --folder data/testvideo
```

1. Make sure all output files from script 1 and 2 are saved in one folder
1. Run the command above, replacing `data/testvideo` with the path to your output folder
1. The files will be concatenated to a single file. The console will show you the path of this file
