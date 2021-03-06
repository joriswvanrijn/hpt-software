import __constants
from utils__general import ask_for_participant_id, ask_for_starting_task, prepare_event_tasks, we_are_not_skipping_task, ask_for_video_id, check_participant_id
from merge_gaze_positions import merge_gaze_positions
from identify_gaps_in_gaze_positions import identify_gaps_in_gaze_positions
from to_lin_time_scale_and_generate_tsv import to_lin_time_scale_and_generate_tsv
from check_calibration_surfaces import check_calibration_surfaces
from rich.progress import Progress, TimeElapsedColumn, BarColumn, TimeRemainingColumn
import time, sys
from utils__console import console
from rich.prompt import Confirm
from utils__general import show_error

# We'll run an analysis for a specific participant, thus we need an ID
participant_id = ask_for_participant_id()
video_id = ask_for_video_id()
starting_task = ask_for_starting_task()
check_participant_id(participant_id, video_id)

# Set up a progress bar
progress_instance = Progress(
    "[progress.description]{task.description}",
    BarColumn(),
    "[progress.percentage]{task.percentage:>3.0f}%",
    TimeRemainingColumn(),
    TimeElapsedColumn(),
)

console.print("[bold yellow]Starting analysis for participant \"{}/{}\" at task {}".format(participant_id, video_id, starting_task))

#### 1) Check ijk surfaces (calibration surfaces) on expected moments
console.print("[cyan]1. Checking ijksurfaces")

if(starting_task == 1):
    check_calibration_surfaces(participant_id, video_id, '{}.json'.format(video_id), console)
    if(not Confirm.ask("May we continue?")):
        show_error('Aborted by user')

with progress_instance as progress:

    # Setting up all tasks (progress bar)
    tasks = prepare_event_tasks(progress)

    #### 2) Merge the gaze_gaze_positions_on_surface_Surface*WB.csv (and dummy)
    if(we_are_not_skipping_task(2, starting_task, progress, tasks)):
        merge_gaze_positions(participant_id, video_id, progress, tasks[0])

    #### 3) Identify (valid) gaps in the gaze positions data
    if(we_are_not_skipping_task(3, starting_task, progress, tasks)):
        identify_gaps_in_gaze_positions(participant_id, video_id, progress, tasks[1])

    #### 4) Interpolate time to linear scale and generate TSV (x y) with linear time
    if(we_are_not_skipping_task(4, starting_task, progress, tasks)):
        to_lin_time_scale_and_generate_tsv(participant_id, video_id, progress, tasks[2])
        # TODO: Filter out everything which is marked as a valid gap

    #### 5) Call REMoDNaV to indentify events
    if(we_are_not_skipping_task(5, starting_task, progress, tasks)):
        progress.print("[red]TODO: call to REMODNAV")