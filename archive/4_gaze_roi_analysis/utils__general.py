import __constants
from genericpath import isdir
from os import mkdir
from utils__console import console
import os.path

def we_are_not_skipping_task(current_task, starting_task, progress, tasks):
    if(current_task < starting_task):
        progress.print('[i bright_black]Skipping task {}... Assuming we already did this.'.format(current_task))
        progress.update(tasks[current_task - 1], total=1, completed=1)

        return False
    else:
        return True

def show_error(message, progress):
    progress.print("[bold red]{}".format(message))
    raise Exception(message)

def ask_for_participant_id():
    id = console.input("Provide the [bold cyan]participant id[/bold cyan] [i bright_black](default: P-022)[/i bright_black]: ") or "P-022"
    return id

def ask_for_video_id():
    file = console.input("Provide the [bold cyan]video ID (e.g. Deel 1)[/bold cyan] (for input folder and both ROI & synchronisation file) [i bright_black](default: Deel1)[/i bright_black]: ") or "Deel1"
    check_rois_files(file)
    return file

def ask_for_starting_task():
    return int(console.input('At [bold cyan]which task[/bold cyan] are we starting? [i bright_black](default: 1)[/i bright_black] ') or "1")

def check_rois_files(file):
    if file == "":
        raise Exception('No ROI file provided')
    elif not os.path.isfile('../rois/{}.csv'.format(file)):
        raise Exception('ROIs file for {}.csv not found'.format(file))
    elif not os.path.isfile('../start_end_frames/synchronisation/{}.json'.format(file)):
        raise Exception('calibration file for {}.json not found'.format(file))

def check_participant_id(id, video_id):
    if id == "":
        raise Exception('No participant ID provided')
    elif not os.path.isdir('{}/{}'.format(__constants.input_folder, id)):
        raise Exception('Input folder for participant {} not found'.format(id))

    if not os.path.isdir('../outputs'.format(id)):
        os.mkdir('../outputs'.format(id))
    if not os.path.isdir('../outputs/{}'.format(id)):
        os.mkdir('../outputs/{}'.format(id))
    if not os.path.isdir('../outputs/{}/{}'.format(id, video_id)):
        os.mkdir('../outputs/{}/{}'.format(id, video_id))

def prepare_aoi_tasks(progress):
     return [
        progress.add_task("[cyan]2. Merging gaze positions", total=20), # 0
        progress.add_task("[cyan]3. Median filter", total=1), # 1
        progress.add_task("[cyan]4. Identifying gaps in gaze positions", total=1), # 2
        progress.add_task("[cyan]5. Identifying hits", total=50), # 3
        progress.add_task("[cyan]6. Identifying entries and exits", total=50), # 4
        progress.add_task("[cyan]7. Generating output", total=9), # 5
     ]

def prepare_event_tasks(progress):
     return [
        progress.add_task("[cyan]2. Merging gaze positions", total=20), # 0
        progress.add_task("[cyan]3. Identifying gaps in gaze positions", total=1), # 1
        progress.add_task("[cyan]4. Interpolate time to linear scale and generate TSV (x y) with linear time", total=1), # 1
        progress.add_task("[cyan]5. Call REMoDNaV to indentify events", total=1), # 1
        # TODO:
     ]