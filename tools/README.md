# Tools

## Overlaying ROIS and gaze positions over a video

```bash
$ python3 overlay_with_roi_and_gaze.py --video="../videos/Validatietaak.mp4" --data="../rois/validatietaak.csv" --gazedata="../inputs/validatietaak-RVR/merged_surfaces_with_gaps.csv" --start_frame=1000
```

## Overlaying ROIS over a video

```bash
$ python3 overlay_with_rois.py --data '../rois/validatietaak.csv' --video '../videos/Validatietaak.mp4'
```

**Usage**

- Run the command above
- The video will be outputted to `video_with_labels.mp4` in the same folder
- Make sure to move this video before creating a new video
- NB: video processing make take a while since every frame has to be processed at full resolution
