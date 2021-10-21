## Input folder
input_folder = '/Users/joris/Development/HPT/hpt-software/inputs' # path on joris machine

## Maxmimum coefficient of linear fit on ijkframes_found per scene
max_coef_lin_fit_ijkframes = 0.3

## Identifying gaps
confidence_treshold = .5 # in %

## Calculating AOI hits
distance_to_screen = 65.06 # in cm 
ppi = 94.34 # px per inch
ppc = ppi/2.54 # px per cm 37,141732283
z = d = distance_d = distance_to_screen_px = distance_to_screen * ppc # in pixels

angle_a = error_angle = 1.5 # in degrees
angle_b = minimal_angle_of_aoi = 0 # in degrees

# ## Identifying entries and exits
# consecutive_0_treshold = 1

# Filter short times between exits and entries
minimal_treshold_entry_exit = 0.1 # in sec
minimal_treshold_dwell = 0.1 # in sec

## Surfaces & screen
total_surface_width = 5760 # in px
total_surface_height = 1200 # in px
screen_middle_y = 600 # in px
screen_middle_x = 2880 # in px

surfaces = {}
surfaces[1] = {'left_border': 0, 'right_border': 691 }
surfaces[2] = {'left_border': 450, 'right_border': 1208 }
surfaces[3] = {'left_border': 1087, 'right_border': 1786 }
surfaces[4] = {'left_border': 1665, 'right_border': 2362 }
surfaces[5] = {'left_border': 2242, 'right_border': 3516 }
surfaces[6] = {'left_border': 3396, 'right_border': 4094 }
surfaces[7] = {'left_border': 3972, 'right_border': 4671 }
surfaces[8] = {'left_border': 4548, 'right_border': 5308 }
surfaces[9] = {'left_border': 5067, 'right_border': 5760 }