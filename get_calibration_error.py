import os.path
import json
from compress_gaze_points import compress_gaze_points

from filter_gaps import filter_gaps


def get_calibration_error(location, recording="000"):
    """
    Calculates and returns the error for given calibration video.
    The function reads the gathered gaze points and compares them to the
    expected locations of the calibration points.
    
    location is the calibrations root folder for a given subject
    recording is the calibration recording folder name eg. "001"
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
    cp_locations = [
        [0.5, 0.5], # Center
        [0.25, 0.25], # Down left
        [0.25, 0.75], # Up left
        [0.75, 0.75], # Up right
        [0.75, 0.25] # Down right
    ]

    # Start calculating the error from the starting frame of the first interval
    current_point = 0

    for row in gaze_points:
        print(row)

    print(points)

if __name__ == "__main__":
    print(get_calibration_error(
        r"C:\Local\siivonek\Data\eye_tracking_data\own_test_data\eyetrack_results\0-f-35\calibrations", "001"))