import os.path
from csv import reader
from math import fabs
import numpy as np

import config as cfg
from compress_gaze_points import compress_gaze_points
from detect_outliers import detect_outliers
from filter_gaps import filter_gaps
from get_calibration_point_intervals import get_calibration_point_intervals



def get_calibration_error(location, recording="000", k=3, threshold=0.02):
    """
    Calculates and returns the error for given calibration video.
    The function reads the gathered gaze points and compares them to the
    expected locations of the calibration points.
    
    Returns gaze error points and outlier point indices as arrays
    
    location is the calibrations root folder for a given subject
    recording is the calibration recording folder name eg. "001"
    k is the number of neighbors in k-NN method. This is used to detect outliers
    threshold is the value used in k-NN method. Points closer to this are considered near neighbors
    """

    csv_file_path = os.path.join(location, recording, "exports")
    subject_dir = os.path.normpath(os.path.join(location, "../"))

    assert (len(os.listdir(csv_file_path)) == 1)  # Make sure there is exactly one export result

    # Load the gaze points from a .csv file and process
    # Also load the provided fixation data
    csv_file_path = os.path.join(csv_file_path, os.listdir(csv_file_path)[0], "surfaces")
    fixation_file_path = ""
    for filename in os.listdir(csv_file_path):
        if filename[0:5] == "gaze_":
            csv_file_path = os.path.join(csv_file_path, filename)
        elif filename[0:10] == "fixations_":
            fixation_file_path = os.path.join(csv_file_path, filename)

    # Read fixations
    fixations = []
    # 0 id, 1 start_timestamp, 2 duration, 3 start_frame, 4 end_frame, 5 norm_pos_x, 6 norm_pos_y,
    # 7 x_scaled, 8 y_scaled, 9 on_srf
    # Indexes to be copied: start & end frames, x & y position
    indexes = [3, 4, 5, 6]
    with open(fixation_file_path) as fixation_csv:
        datareader = reader(fixation_csv)
        # Skip header
        datareader.__next__()
        for row in datareader:
            fixations.append([row[i] for i in indexes])

    gaze_points_tmp = filter_gaps(csv_file_path, 10)

    # Calculate the averages of points in the same frame
    gaze_points = compress_gaze_points(gaze_points_tmp)

    # Get the calibration point intervals for this video
    calibrations_dir = os.path.join(subject_dir, "calibrations")
    points = get_calibration_point_intervals(calibrations_dir, recording)

    gaze_error = {}
    fixation_error = {}
    current_point = 0
    error_sum_x = 0
    error_sum_y = 0

    # Go through each point interval and calculate gaze error
    for point in points:
        # Gather the gaze points between interval start and end frames
        interval = [i for i in gaze_points if (i[0] >= point[0] and i[0] <= point[1])]

        # Gather fixations inside current interval
        fixation_count = 0
        current_fixations = []
        for fixation in fixations:
            if int(fixation[0]) > point[0] and int(fixation[0]) < point[1]:
                fixation_count += 1
                tmp = fixation

                # Convert from string
                tmp[0] = int(tmp[0])  # Start frame
                tmp[1] = int(tmp[1])  # End frame
                tmp[2] = float(tmp[2])  # xpos
                tmp[3] = float(tmp[3])  # ypos

                # We also need the point visibility start and end for later visualization
                tmp.append(point[0])  # Calibration point start frame
                tmp.append(point[1])  # End frame

                # Cut the fixation end to match calibration point end
                if tmp[1] > point[1]:
                    tmp[1] = point[1]

                # Calculate error
                tmp[2] = tmp[2] - cfg.CALIBRATION_POINT_LOCATIONS[current_point][0]
                tmp[3] = tmp[3] - cfg.CALIBRATION_POINT_LOCATIONS[current_point][1]
                current_fixations.append(tmp)

        fixation_error[cfg.CALIBRATION_POINT_NAMES[current_point]] = current_fixations

        error_x = []
        error_y = []
        error_comb = []
        for row in interval:
            # Subtract the calibration point center from the measured value
            # This way the error will be as follows:
            # On x axis the error will be positive if the measured point is to the right of the CP center
            # On y axis the error will be positive if the measured point is above the CP center
            error_x_tmp = row[1] - cfg.CALIBRATION_POINT_LOCATIONS[current_point][0]
            error_y_tmp = row[2] - cfg.CALIBRATION_POINT_LOCATIONS[current_point][1]
            error_sum_x += error_x_tmp
            error_sum_y += error_y_tmp
            error_x.append(error_x_tmp)
            error_y.append(error_y_tmp)
            error_comb.append(fabs(error_x_tmp) + fabs(error_y_tmp))

        # Check points for outliers
        points = np.column_stack((error_x, error_y))
        outlier_indices = detect_outliers(points)
        # Group error values together by calibration point index
        gaze_error[cfg.CALIBRATION_POINT_NAMES[current_point]] = [error_x, error_y, error_comb, outlier_indices]

        error_sum_x = 0
        error_sum_y = 0
        current_point += 1

    return gaze_error, fixation_error


if __name__ == "__main__":
    pass
