import os.path
import json
from csv import reader
from math import fabs
import pprint

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
    # 0 id, 1 start_timestamp, 2 duration, 3 start_frame, 4 end_frame, 5 norm_pos_x, 6 norm_pos_y, 7 x_scaled, 8 y_scaled, 9 on_srf
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
    fixation_error = {}
    current_point = 0
    error_sum_x = 0
    error_sum_y = 0

    print("\nTotal fixations: " + str(len(fixations)))
    print(fixations)
    # Go through each point interval and calculate gaze error
    for point in points:
        # Gather the gaze points between interval start and end frames
        interval = [ i for i in gaze_points if(i[0] >= point[0] and i[0] <= point[1])]

        # Gather fixations inside current interval
        fixation_count = 0
        current_fixations = []
        for fixation in fixations:
            if int(fixation[0]) > point[0] and int(fixation[0]) < point[1]:
                fixation_count += 1
                tmp = fixation
                # Convert from string
                tmp[0] = int(tmp[0])
                tmp[1] = int(tmp[1])
                tmp[2] = float(tmp[2])
                tmp[3] = float(tmp[3])
                # We also need the point visibility start and end for later visualization
                tmp.append(point[0])
                tmp.append(point[1])

                if tmp[1] > point[1]:
                    tmp[1] = point[1]
                # Calculate error
                tmp[2] = tmp[2] - cp_locations[current_point][0]
                tmp[3] = tmp[3] - cp_locations[current_point][1]
                current_fixations.append(tmp)

        print("Fixations in interval (" + str(point[0]) + "-" + str(point[1]) + "): " + str(fixation_count))
        fixation_error[current_point] = current_fixations

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

        # Calculate separate fixation error


    return gaze_error, fixation_error

if __name__ == "__main__":
    pp = pprint.PrettyPrinter(indent=2)
    gaze_error, fixation_error = get_calibration_error(
        r"C:\Local\siivonek\Data\eye_tracking_data\own_test_data\eyetrack_results\23-f-25\calibrations", "001")
    pp.pprint(gaze_error)
    pp.pprint(fixation_error)
