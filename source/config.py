# Config for eye tracking data processing

# List of test subjects to ignore
# Add subjects with defective data
ignore_person = ['0-f-35',
                 '16-f-43',
                 '28-f-23',
                 '32-f-26',
                 '33-f-36']

# A calibration check is assumed to be shown after every N videos
# This is used to insert calibrations into the timeline since
# calibrations do not show up in the experiment log file
calibration_check_interval = 5

# The directory which contains the results for each subject
results_directory = r"D:\actual_eyetrack_results"