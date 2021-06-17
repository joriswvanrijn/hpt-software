from utils import ask_for_participant_id
from rich.progress import Progress
import time

# We'll run an analysis for a specific participant, thus we need an ID
participant_id = ask_for_participant_id()

with Progress() as progress:

    task1 = progress.add_task("[cyan]1. Merging gaze positions", total=50)
    task2 = progress.add_task("[cyan]2. Identifying gaps in gaze positions", total=50)
    task3 = progress.add_task("[cyan]3. Identifying hits", total=50)
    task4 = progress.add_task("[cyan]4. Identifying entries and exits", total=50)
    task5 = progress.add_task("[cyan]5. Generating output", total=50)

    while not progress.finished:
        progress.update(task1, advance=0.5)
        time.sleep(0.02)

# 1) Merge the gaze_gaze_positions_on_surface_Surface*WB.csv (and dummy)
# merge_gaze_positions(participant_id)

# 2) Identify (valid) gaps in the gaze positions data
# identify_gaps_in_gaze_positions(participant_id)

# 3) With the ROIs and the GPs: identify hits in the ROIs
# identify_hits(participant_id)

# 4) Identify entries and exits for all ROIs
# identify_entries_and_exits(participant_id)

# 5) Generate an output.csv to use in further analysis
# generate_output(participant_id)