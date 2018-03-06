import os
import numpy as np
import time

import matplotlib.pyplot as plt

from filter_gaps import filter_gaps
from get_starting_frame import get_starting_frame

# Index definitions
WORLD_TIMESTAMP = 0
WORLD_FRAME_IDX = 1
GAZE_TIMESTAMP = 2
X_NORM = 3
Y_NORM = 4
X_SCALED = 5
Y_SCALED = 6
ON_SRF = 7
CONFIDENCE = 8

def error_visualization(test_dir):
    """
    Visualizes calibration error for given test subject.
    
    :param test_dir: 
    :return: 
    """
    calibrations_root = os.path.join(test_dir, "calibrations")

    # Get calibration folders
    calibrations = next(os.walk(calibrations_root))[1]

    # Last 8 entries will be the calibration check videos
    # TODO: Fix this line to include last 8 entries after testing
    for cdir in [calibrations[1],]:
        print("Processing calibration " + cdir)
        # Get the starting frame for current video
        start_frame = get_starting_frame(calibrations_root, cdir, threshold=200)

        csv_file_path = os.path.join(calibrations_root, cdir, "exports")
        assert (len(os.listdir(csv_file_path)) == 1)  # Make sure there is exactly one export result

        csv_file_path = os.path.join(csv_file_path, os.listdir(csv_file_path)[0], "surfaces")
        for item in os.listdir(csv_file_path):
            if item[0:5] == "gaze_":
                csv_file_path = os.path.join(csv_file_path, item)

        final_data = filter_gaps(csv_file_path, start_frame)

        # Draw a plot
        #plt.plot([row[1] for row in filtered_data], [row[2] for row in filtered_data], 'b.')
        #plt.plot([row[1] for row in eliminated_data], [row[2] for row in eliminated_data], 'r.')
        #plt.plot()
        #plt.legend(['x_norm', 'y_norm'])
        #plt.axis('off')
        #plt.axis([plot_x_start, plot_x_end, 0, 1])
        #plt.axis('scaled')
        #plt.show()


if __name__ == '__main__':
    # Test data root folder
    root = r'C:\Local\siivonek\Data\eye_tracking_data\own_test_data\eyetrack_results'
    test_subject = "6-m-23"

    dir = os.path.join(root, test_subject)

    error_visualization(dir)