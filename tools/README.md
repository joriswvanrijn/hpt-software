# Tools

## Overlaying ROIS and gaze positions over a video

```bash
python3 overlay_with_roi_and_gaze.py --video="../inputs/Deel1.mp4" --data="../rois/deel1.csv" --participant="../../pilot-data/P-022/Deel1" --start_frame=800

python3 overlay_multiple_participants.py --video="../inputs/Deel1.mp4" --data="../rois/deel1.csv" --deel="Deel1" --start_frame=800
```

## Overlaying ROIS over a video

```bash
python3 overlay_with_rois.py --video="../inputs/Deel1.mp4" --data="../rois/deel1.csv" --start_frame=1000
```

**Usage**

- Run the command above
- The video will be outputted to `video_with_labels.mp4` in the same folder
- Make sure to move this video before creating a new video
- NB: video processing make take a while since every frame has to be processed at full resolution
