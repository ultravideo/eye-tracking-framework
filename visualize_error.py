# Visualize gaze point error compared to calibration point

import json
import os.path

root = r"C:\Local\siivonek\Data\eye_tracking_data\own_test_data\eyetrack_results"
datafile_path = os.path.join(root, "data.json")

# Load calibration point intervals
with open(datafile_path) as file:
    cp_data = json.load(file)

