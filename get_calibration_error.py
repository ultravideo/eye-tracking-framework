import os.path
import json
from math import fabs

from compress_gaze_points import compress_gaze_points
from filter_gaps import filter_gaps
from detect_outliers import detect_outliers


def get_calibration_error(location, recording="000", k = 3, threshold = 0.02):
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
    subject = os.path.basename(subject_dir)

    assert (len(os.listdir(csv_file_path)) == 1)  # Make sure there is exactly one export result

    # Load the gaze points from a .csv file and process
    csv_file_path = os.path.join(csv_file_path, os.listdir(csv_file_path)[0], "surfaces")
    for filename in os.listdir(csv_file_path):
        if filename[0:5] == "gaze_":
            csv_file_path = os.path.join(csv_file_path, filename)

    gaze_points_tmp = filter_gaps(csv_file_path, 10)

    # Calculate the averages of points in the same frame
    gaze_points = compress_gaze_points(gaze_points_tmp)

    # Load the calibration point intervals
    json_file_path = os.path.normpath(os.path.join(location, "../../cp_intervals_dict.json"))

    with open(json_file_path) as cp_data:
        cp_intervals = json.load(cp_data)
        cp_data.close()

    # Get the calibration point intervals for this video
    points = cp_intervals[subject][recording]

    # Expected calibration point locations
    # Note, in the eye capture software, y-axis is positive upwards
    # In openCV, it's positive downwards
    # Old values
    """
    cp_locations = [
        [0.5, 0.5], # Center
        [0.25, 0.25], # Down left
        [0.25, 0.75], # Up left
        [0.75, 0.75], # Up right
        [0.75, 0.25] # Down right
    ]
    """

    cp_locations = [
        [0.5, 0.5],  # Center
        [114/384, 1/3],  # Down left
        [114/384, 2/3],  # Up left
        [270/384, 2/3],  # Up right
        [270/384, 1/3]  # Down right
    ]



    gaze_error = []
    current_point = 0
    error_sum_x = 0
    error_sum_y = 0

    # Go through each point interval and calculate gaze error
    for point in points:
        interval = [ i for i in gaze_points if(i[0] >= point[0] and i[0] <= point[1])]
        error_x = []
        error_y = []
        error_comb = []
        for row in interval:
            # Subtract the calibration point center from the measured value
            # This way the error will be as follows:
            # On x axis the error will be positive if the measured point is to the right of the CP center
            # On y axis the error will be positive if the measured point is above the CP center
            error_x_tmp = row[1] - cp_locations[current_point][0]
            error_y_tmp = row[2] - cp_locations[current_point][1]
            error_sum_x += error_x_tmp
            error_sum_y += error_y_tmp
            error_x.append(error_x_tmp)
            error_y.append(error_y_tmp)
            error_comb.append(fabs(error_x_tmp)+fabs(error_y_tmp))

            #print("Error x: " +str(error_x_tmp) + " y: " + str(error_y_tmp))

        # Check points for outliers using k-NN
        outlier_indices = detect_outliers(error_comb)
        # Group error values together by calibration point index
        gaze_error.append([error_x, error_y, error_comb, outlier_indices])



        print("Outliers detected: " + str(len(outlier_indices)))
        if len(outlier_indices) > 0:
            print(outlier_indices)

        error_sum_x = 0
        error_sum_y = 0
        current_point += 1

    return gaze_error

if __name__ == "__main__":
    print(get_calibration_error(
        r"C:\Local\siivonek\Data\eye_tracking_data\own_test_data\eyetrack_results\0-f-35\calibrations", "001"))