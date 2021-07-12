# ROI Hinting

_Folder: `/1_roi_hinting`_

The goal of this part of the HPT toolset is to let experts identify MUST and MAY be seen hazards. This folder contains a Laravel applicaton. It should be uploaded to a webserver.

**Usage:**

1. When navigating to the path of the server, users may click on a specified video
1. The clicks on the video are stored in a database and may be exported
1. Those exported files can be used to generate a video with a python script

## Notes

-   Install the app like a normal Laravel application (see [official Laravel docs](https://laravel.com/docs/8.x/installation))
-   Video files are not included in the repo, they must be seperately uploaded to `./storage/app/public/videos/`
-   Data files will be saved to `./storage/app/public/data/`
-   Log files can be found in `./storage/app/logs/`

### Video compression used

```shell
ffmpeg -i source.mp4 -c:v libvpx-vp9 -b:v 1M -c:a libopus -b:a 128k target.webm
# old: ffmpeg -i input.mp4 -c:v libvpx-vp9 -crf 30 -b:v 0 -b:a 128k -c:a libopus output.webm
```
