from random import sample
import pandas as pd
import os
from remodnav import main

# Variables
gp_path = '/Users/joris/Development/HPT/dynamic-aoi-toolkit/data/input-gp/P-033/val/gp.csv'
output_path = './outputs/gp.tsv'
px2deg = 0.017361783368346345
sample_rate = 240

# csv to tsv
gp_df = pd.read_csv(gp_path) 
gp_df[['x', 'y']].to_csv(output_path, sep="\t", index=False, header=False)

# call remodnav
cmd = 'remodnav {} ./outputs/events.tsv {} {} --savgol-length 0.021'.format(output_path, px2deg, sample_rate)
print('executing {}'.format(cmd))
os.system(cmd)