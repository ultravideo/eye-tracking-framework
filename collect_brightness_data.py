# Gather the calibration points brightness from each calibration video

import os
import json
from analyze_cp_brightness import analyze_cp_brightness

root = r"C:\Local\siivonek\Data\eye_tracking_data\own_test_data\eyetrack_results"
export_path_root = os.path.join(root, "export")

# create test data folder if it doesn't exists
if not os.path.isdir(export_path_root):
    os.makedirs(export_path_root)
# Go through all experiment folders
# Each folder contains all data for one experiment instance

data = []

for dir in os.listdir(root):
    # Check if item is an actual directory
    if os.path.isdir(os.path.join(root, dir)):
        subject_dir = os.path.join(root, dir)
        calibs_dir = os.path.join(subject_dir, "calibrations")

        print("Processing subject " + subject_dir)

        # Check if calibrations actually exist
        if os.path.isdir(calibs_dir):
            calibrations = next(os.walk(calibs_dir))[1]
            # Go through the last eight calibrations
            # The first 1-3 are the initial calibrations, which do not interest us
            cp_brightness = []
            for calibration in calibrations[-8:]:
                print("Processing calibration " + calibration)
                cp_brightness.append([calibration, analyze_cp_brightness(calibs_dir, calibration)])

            print("Collected:")
            print(cp_brightness)
            data.append([dir, cp_brightness])

        else:
            print("Calibrations for subject " + dir + " do not exist")
    else:
        print(dir + " is not a directory")

# Dump data as JSON
with open(os.path.join(root, "cp_brightness.json"), 'w') as file:
    json.dump(data, file)
    file.close()
