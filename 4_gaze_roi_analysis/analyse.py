import __constants
from utils__general import ask_for_participant_id, ask_for_starting_task, prepare_tasks, we_are_not_skipping_task, ask_for_rois_id
from merge_gaze_positions import merge_gaze_positions
from identify_gaps_in_gaze_positions import identify_gaps_in_gaze_positions
from identify_hits import identify_hits
from identify_entries_and_exits import identify_entries_and_exits
from generate_output import generate_output
from check_calibration_surfaces import check_calibration_surfaces
from rich.progress import Progress, TimeElapsedColumn, BarColumn, TimeRemainingColumn
import time, sys

# We'll run an analysis for a specific participant, thus we need an ID
participant_id = ask_for_participant_id()
rois_id = ask_for_rois_id()
starting_task = ask_for_starting_task()

# Set up a progress bar
progress_instance = Progress(
    "[progress.description]{task.description}",
    BarColumn(),
    "[progress.percentage]{task.percentage:>3.0f}%",
    TimeRemainingColumn(),
    TimeElapsedColumn(),
)

with progress_instance as progress:

    # Setting up all tasks
    tasks = prepare_tasks(progress)
    progress.print("[bold yellow]Starting analysis for participant \"{}\" at task {}".format(participant_id, starting_task))

    #### 1) Check ijk surfaces (calibration surfaces) on expected moments
    if(we_are_not_skipping_task(1, starting_task, progress, tasks)):
        check_calibration_surfaces(participant_id, '{}.json'.format(rois_id), progress, tasks[0])

    #### 2) Merge the gaze_gaze_positions_on_surface_Surface*WB.csv (and dummy)
    if(we_are_not_skipping_task(2, starting_task, progress, tasks)):
        merge_gaze_positions(participant_id, progress, tasks[1])

    #### 3) Identify (valid) gaps in the gaze positions data
    if(we_are_not_skipping_task(3, starting_task, progress, tasks)):
        identify_gaps_in_gaze_positions(participant_id, progress, tasks[2])

    #### 4) With the ROIs and the GPs: identify hits in the ROIs
    if(we_are_not_skipping_task(4, starting_task, progress, tasks)):
        identify_hits(participant_id, '{}.csv'.format(rois_id), progress, tasks[3])

    #### 5) Identify entries and exits for all ROIs
    if(we_are_not_skipping_task(5, starting_task, progress, tasks)):
        identify_entries_and_exits(participant_id, '{}.csv'.format(rois_id), progress, tasks[4])

    #### 6) Generate an output.csv to use in further analysis
    if(we_are_not_skipping_task(6, starting_task, progress, tasks)):
        generate_output(participant_id, '{}.csv'.format(rois_id), progress, tasks[5])

    progress.print('[bold green]Done!')