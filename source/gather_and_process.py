import sys
import os
import json
import numpy as np

from get_calibration_folders import get_calibration_folders
from get_calibration_error import get_calibration_error
from calculate_metadata import calculate_metadata


def gather_and_process(root, destination, width=3840, height=2160):
    """
        Gathers and processes the gaze data.        

        Root is the root folder which contains experiment results     
        Destination is the folder name where the exported .json is put
        Width and height are the pixel dimensions of the test monitor
        It is found under the exports folder, which is in the parent folder of root
        """

    export_root = os.path.abspath(os.path.join(root, "..", "exports"))

    # Create exports directory if it doesn't exist
    if not os.path.exists(export_root):
        os.makedirs(export_root)

    folders = get_calibration_folders(root)

    # Gather gaze points, process and save results.
    results = {}
    average_results = {}
    datafolder = os.path.join(export_root, destination)
    if not os.path.isdir(datafolder):
        os.makedirs(datafolder)

    datafile = os.path.join(export_root, destination, "processed_gaze_points.json")
    # Averages for gaze error and fixations
    averages_file = os.path.join(export_root, destination, "processed_averages.json")
    if not os.path.isfile(datafile):
        for subject, calibs in folders.items():
            calibrations_path = os.path.join(root, subject, "calibrations")

            calib_dict = {}
            average_dict = {}
            # Iterate through last eight entries. First 1-3 folders can be initial calibrations
            for calibration in calibs[-8:]:
                tmp = {}
                avg_tmp = {}
                # Gaze error will be in format:
                # { calibration_point: [ error_x[], error_y[], error_combined[], outlier_indices[] ] }
                # Fixation error will be in format:
                # { calibration_point: [ start frame, end frame, error x, error y, cp start frame, cp end frame ] }
                gaze_error, fixation_error = get_calibration_error(calibrations_path, calibration)
                tmp['gaze_error'] = gaze_error
                tmp['fixation_error'] = fixation_error

                calib_dict[calibration] = tmp

                # Calculate averages for raw gaze points and fixations
                gaze_tmp = {}
                for cp, values in gaze_error.items():
                    error_avg_x = 0
                    error_avg_y = 0
                    error_sum_x = 0
                    error_sum_y = 0
                    length = len(values[0])
                    outliers = len(values[3])
                    # Check if x and y length is the same
                    if length == len(values[1]):
                        for i in range(length):
                            # Skip if index is marked as outlier
                            if i not in values[3]:
                                error_sum_x += values[0][i]
                                error_sum_y += values[1][i]

                        if length > outliers:
                            error_avg_x = error_sum_x / (length - outliers)
                            error_avg_y = error_sum_y / (length - outliers)
                    else:
                        print("Error, x and y dimension mismatch")

                    gaze_tmp[cp] = [error_avg_x, error_avg_y, error_avg_x * width, error_avg_y * height]

                avg_tmp['gaze_error'] = gaze_tmp

                fixation_tmp = {}
                for cp, values in fixation_error.items():
                    total_length = 0
                    weights = []
                    x_coords = []
                    y_coords = []
                    if values:
                        for fixation in values:
                            total_length += fixation[1] - fixation[0]

                        for fixation in values:
                            x_coords.append(fixation[2])
                            y_coords.append(fixation[3])
                            weights.append((fixation[1] - fixation[0]) / total_length)

                        avg_x = np.average(x_coords, weights=weights)
                        avg_y = np.average(y_coords, weights=weights)
                        fixation_tmp[cp] = [avg_x, avg_y, avg_x * width, avg_y * height]
                    else:
                        fixation_tmp[cp] = []
                avg_tmp['fixation_error'] = fixation_tmp

                average_dict[calibration] = avg_tmp

            results[subject] = calib_dict
            average_results[subject] = average_dict

        # Dump data
        with open(datafile, 'w') as file:
            json.dump(results, file)
            file.close()

        with open(averages_file, 'w') as file:
            json.dump(average_results, file)
            file.close()

        # Calculate line fits and statistical data for average values for each subject
        calculate_metadata(root, destination, average_results)



if __name__ == "__main__":
    # Check command line arguments
    if len(sys.argv) < 3:
        print("Need at least two arguments: data root folder and destination folder")
        print("Destination is relative to root: ../exports/<destination>")
    else:
        gather_and_process(sys.argv[1], sys.argv[2])
