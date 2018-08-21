# Config for eye tracking data processing

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