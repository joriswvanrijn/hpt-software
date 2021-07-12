# Video preparation (burn QR codes to video)

The goal of this part of the HPT toolset is to burn QR codes to a video so it can be used in the trials.

## Burn QR codes

```bash
$ python3 burn_qrs.py --name="../videos/vid.mp4" --cols=8 --rows=4 --default-scale=2
$ python3 burn_qrs.py --name="../videos/vid.mp4" --cols=8 --rows=4 --default-scale=2 --large-scale=4 --large-scale-indeces=16,18,17,19
```

**Usage:**

- In `/output` it will output the video with burned QR codes and it will provide a png with the QR codes
