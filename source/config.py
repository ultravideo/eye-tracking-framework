# Config for eye tracking data processing

from os.path import isdir
from os.path import join

# The path to original video files used in experiment
TEST_VIDEO_FOLDER = r"D:\Raw_Files\eye_tracking_final_sequences_y4m"

# List of test subjects to ignore
# Add subjects with defective data
IGNORE_PERSON = ['0-f-35',
                 '16-f-43',
                 '28-f-23',
                 '32-f-26',
                 '33-f-36']

# A calibration check is assumed to be shown after every N videos
# This is used to insert calibrations into the timeline since
# calibrations do not show up in the experiment log file
CALIBRATION_CHECK_INTERVAL = 5

# The directory which contains the results for each subject
RESULTS_DIRECTORY = r"D:\actual_eyetrack_results"

# The amount of calibration points in calibration checks
CALIBRATION_POINTS_AMOUNT = 5

# The positions of calibration points, number of coordinate sets must be equal to
# calibration_points_amount
# The coordinate sets must be in the same order as the calibration points appear
# The coordinates are relative to screen dimensions
# Bottom left = 0, 0, top right = 1, 1
# Note: the correction factor is calculated based on the four corner calibration points
# in indexes 1 through 4 by default. If these are changed, correct the indexes
# def get_transform_matrix_at_time() in get_correction_func.py
CALIBRATION_POINT_LOCATIONS = [
    [0.5, 0.5],  # Center
    [114 / 384, 1 / 3],  # Down left
    [114 / 384, 2 / 3],  # Up left
    [270 / 384, 2 / 3],  # Up right
    [270 / 384, 1 / 3]]  # Down right

# Give identifiable names to each calibration point
CALIBRATION_POINT_NAMES = [
    "center",
    "bottom_left",
    "top_left",
    "top_right",
    "bottom_right"]

# The time each calibration check takes in seconds
CALIBRATION_CHECK_TIME = 10.0

# CLUSTERING variables

# During clustering of gaze points, if most data points fit inside this threshold window, clustering is not needed
# These values are calculated based on the physical screen dimensions of the monitor used in the experiment,
# the distance between the subject and the screen, and the natural error caused by eye tracker and human vision
# The screen dimensions: width = 0.5816 m, height = 0.32715 m
# The assumed cumulative error of eye tracker and human vision ~= 1 degree
# Change these values based on your eye tracker properties and experiment setup
CLUSTER_THRESHOLD_WIDTH = 0.041
CLUSTER_THRESHOLD_HEIGHT = 0.072

# If this percentage of data points is inside the clustering threshold window, clustering is not needed
CLUSTER_PERCENTAGE_THRESHOLD = 0.9

# Try to find the optimal number of clusters between 2 and this maximum value
# Bigger numbers increase processing time.
MAX_CLUSTERS = 5

# CLUSTERING - END

# GAP FILTERING variables

# If time between two gaze data points is longer than this, there's a missing measurement
GAZE_STAMP_THRESHOLD = 0.0043
# If there are more than N missing measurements within GAP_THRESHOLD (seconds), consider the area as invalid
GAP_THRESHOLD = 0.1
MISSING_MEASUREMENT_THRESHOLD = 5
# This amount in seconds is removed before and after a detected gap
BLINK_REMOVE_THRESHOLD = 0.2

# GAP FILTERING - END

# Path to file used to store the visibility intervals of calibration points in calibration checks for all subjects
# If this file does not exist, the intervals will be calculated before the actual processing will start
INTERVALS_FILE_NAME = "cp_intervals.json"
CALIBRATION_POINT_INTERVALS_PATH = join(RESULTS_DIRECTORY, INTERVALS_FILE_NAME)


# Check validity of config values. Return 'False' if invalid values found
def config_check():
    if not isdir(TEST_VIDEO_FOLDER):
        print("TEST_VIDEO_FOLDER:", TEST_VIDEO_FOLDER, "is not a directory or does not exist.")
        return False

    if not isdir(RESULTS_DIRECTORY):
        print("RESULTS_DIRECTORY:", RESULTS_DIRECTORY, "is not a directory or does not exist.")
        return False

    if len(CALIBRATION_POINT_LOCATIONS) != 5:
        print("Number of entries in CALIBRATION_POINT_LOCATIONS do not match CALIBRATION_POINTS_AMOUNT.")
        return False

    if len(CALIBRATION_POINT_NAMES) != 5:
        print("Number of entries in CALIBRATION_POINT_NAMES do not match CALIBRATION_POINTS_AMOUNT.")
        return False

    if CALIBRATION_CHECK_TIME < 0:
        print("CALIBRATION_CHECK_TIME must be positive")
        return False

    if CLUSTER_THRESHOLD_WIDTH < 0 or CLUSTER_THRESHOLD_WIDTH > 1.0:
        print("CLUSTER_THRESHOLD_WIDTH must be between 0 and 1")
        return False

    if CLUSTER_THRESHOLD_HEIGHT < 0 or CLUSTER_THRESHOLD_HEIGHT > 1.0:
        print("CLUSTER_THRESHOLD_HEIGHT must be between 0 and 1")
        return False

    if CLUSTER_PERCENTAGE_THRESHOLD < 0 or CLUSTER_PERCENTAGE_THRESHOLD > 1.0:
        print("CLUSTER_PERCENTAGE_THRESHOLD must be between 0 and 1")
        return False

    if MAX_CLUSTERS < 2:
        print("MAX_CLUSTERS must be at least 2")
        return False

    return True
