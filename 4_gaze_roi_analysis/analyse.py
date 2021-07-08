import __constants
from utils import ask_for_participant_id, ask_for_starting_task, prepare_tasks, we_are_not_skipping_task
from merge_gaze_positions import merge_gaze_positions
from identify_gaps_in_gaze_positions import identify_gaps_in_gaze_positions
from rich.progress import Progress
import time, sys

# We'll run an analysis for a specific participant, thus we need an ID
participant_id = ask_for_participant_id()
starting_task = ask_for_starting_task()

# Set up a progress bar
with Progress() as progress:

    # Setting up all tasks
    tasks = prepare_tasks(progress)
    progress.print("[bold yellow]Starting analysis for participant \"{}\" at task {}".format(participant_id, starting_task))

    #### 1) Merge the gaze_gaze_positions_on_surface_Surface*WB.csv (and dummy)
    if(we_are_not_skipping_task(1, starting_task, progress, tasks)):
        merge_gaze_positions(participant_id, progress, tasks[0])

    #### 2) Identify (valid) gaps in the gaze positions data
    if(we_are_not_skipping_task(2, starting_task, progress, tasks)):
        identify_gaps_in_gaze_positions(participant_id, progress, tasks[1])

    #### 3) With the ROIs and the GPs: identify hits in the ROIs
    # identify_hits(participant_id)

    #### 4) Identify entries and exits for all ROIs
    # identify_entries_and_exits(participant_id)

# 5) Generate an output.csv to use in further analysis
# generate_output(participant_id)