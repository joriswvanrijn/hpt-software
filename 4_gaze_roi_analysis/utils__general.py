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
    id = console.input("Provide the [bold cyan]participant id[/bold cyan] [i bright_black](default: validatietaak-RVR)[/i bright_black]: ") or "validatietaak-RVR"
    check_participant_id(id)
    return id

def ask_for_rois_file():
    file = console.input("Provide the [bold cyan]ROIs file[/bold cyan] [i bright_black](default: validatietaak.csv)[/i bright_black]: ") or "validatietaak.csv"
    check_rois_file(file)
    return file

def ask_for_starting_task():
    return int(console.input('At [bold cyan]which task[/bold cyan] are we starting? [i bright_black](default: 1)[/i bright_black] ') or "1")

def check_rois_file(file):
    if file == "":
        raise Exception('No ROI file provided')
    elif not os.path.isfile('../rois/{}'.format(file)):
        raise Exception('ROIs file for {} not found'.format(file))

def check_participant_id(id):
    if id == "":
        raise Exception('No participant ID provided')
    elif not os.path.isdir('../inputs/{}'.format(id)):
        raise Exception('Input folder for participant {} not found'.format(id))

    if not os.path.isdir('../outputs'.format(id)):
        os.mkdir('../outputs'.format(id))
    if not os.path.isdir('../outputs/{}'.format(id)):
        os.mkdir('../outputs/{}'.format(id))

def prepare_tasks(progress):
     return [
        progress.add_task("[cyan]1. Merging gaze positions", total=20),
        progress.add_task("[cyan]2. Identifying gaps in gaze positions", total=50),
        progress.add_task("[cyan]3. Identifying hits", total=50),
        progress.add_task("[cyan]4. Identifying entries and exits", total=50),
        progress.add_task("[cyan]5. Generating output", total=9),
     ]