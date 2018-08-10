import os
import math
import numpy as np
import time

import matplotlib.pyplot as plt

from filter_gaps import filter_gaps
from get_starting_frame import get_starting_frame
from get_starting_frame import get_calibration_point_intervals

# Definitions
FIXATION_TOLERANCE = 0.1  # How much gaze is allowed to vary during a fixation


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
    for cdir in [calibrations[1], ]:
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

        # From final data, 5 fixations must be found
        # A steady segment where gaze x- and y-coordinates do not fluctuate
        # is considered a valid fixation.

        x = []
        y = []
        fixations = []
        previous_point = 0
        fixation_start = 0
        fixation_end = 0
        fixation_length = 0
        written = False

        for item in final_data:
            x.append(item[1])
            point = math.sqrt(float(item[2]) ** 2 + float(item[3]) ** 2)
            y.append(point)

            if previous_point == 0:
                fixation_start = item[1]
                fixation_end = item[1]
                fixation_length += 1
            else:
                if math.fabs(previous_point - point) > FIXATION_TOLERANCE:
                    # Difference between the two points is too great, end fixation
                    fixation_end = item[1]
                    fixations.append([fixation_length, fixation_start, fixation_end])
                    written = True
                    fixation_start = fixation_end
                    fixation_length = 1
                else:
                    # Difference is within tolerance, continue fixation
                    fixation_end = item[1]
                    fixation_length += 1
                    written = False

            previous_point = point

        if not written:
            fixations.append([fixation_length, fixation_start, fixation_end])
        print("Fixations found: " + str(len(fixations)))
        for fixation in fixations:
            print("Length: " + str(fixation[0]) + " Time " + str(fixation[1]) + " - " + str(fixation[2]))

            # plt.plot(x, y)
            # plt.axis('off')
            # plt.show()


if __name__ == '__main__':
    # Test data root folder
    root = r'C:\Local\siivonek\Data\eye_tracking_data\own_test_data\eyetrack_results'
    test_subject = "6-m-23"

    dir = os.path.join(root, test_subject)

    error_visualization(dir)
