# Check and log the start and end times of all calibration points in all calibration videos
import os
import json
from get_calibration_point_intervals import get_calibration_point_intervals

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
            # The first one is the initial calibration, which does not interest us
            times = []
            for calibration in calibrations[-8:]:
                print("Processing calibration " + calibration)
                times.append([calibration, get_calibration_point_intervals(calibs_dir, calibration)])

            data.append([dir, times])

        else:
            print("Calibrations for subject " + dir + " do not exist")
    else:
        print(dir + " is not a directory")

# Dump data as JSON
with open(os.path.join(root, "data.json"), 'w') as file:
    json.dump(data, file)
    file.close()
