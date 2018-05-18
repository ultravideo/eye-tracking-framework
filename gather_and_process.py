import sys
import os
import json

from get_calibration_folders import get_calibration_folders
from get_calibration_error import get_calibration_error


def gather_and_process(root, destination):
    """
        Gathers and processes the gaze data.        

        Root is the root folder which contains experiment results     
        Destination is the folder name where the exported .json is put.
        It is found under the exports folder, which is in the parent folder of root
        """

    export_root = os.path.abspath(os.path.join(root, "..", "exports"))

    # Create exports directory if it doesn't exist
    if not os.path.exists(export_root):
        os.makedirs(export_root)

    folders = get_calibration_folders(root)

    # Gather gaze points, process and save results.
    results = {}
    datafile = os.path.join(export_root, destination, "processed_gaze_points.json")
    if not os.path.isfile(datafile):
        # File does not exist. Gather all data
        for subject, calibs in folders.items():
            calibrations_path = os.path.join(root, subject, "calibrations")

            calib_dict = {}
            for calibration in calibs[-8:]:
                tmp = {}
                # Gaze error will be in format:
                # { calibration_point: [ error_x[], error_y[], error_combined[], outlier_indices[] ] }
                # Fixation error will be in format:
                # { calibration_point: [ start frame, end frame, error x, error y, cp start frame, cp end frame ] }
                gaze_error, fixation_error = get_calibration_error(calibrations_path, calibration)
                tmp['gaze_error'] = gaze_error
                tmp['fixation_error'] = fixation_error

                calib_dict[calibration] = tmp

            results[subject] = calib_dict

        # Dump data
        with open(datafile, 'w') as file:
            json.dump(results, file)

if __name__ == "__main__":
    # Check command line arguments
    if len(sys.argv) < 3:
        print("Need at least two arguments: data root folder and destination folder")
    else:
        gather_and_process(sys.argv[1], sys.argv[2])
