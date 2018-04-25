# Visualize gaze point error compared to calibration point

import os.path
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import json
import pprint
import numpy as np
import sys

from get_calibration_error import get_calibration_error
from get_calibration_folders import get_calibration_folders

def visualize_error(root, destination):
    """
    Draws plots for data and writes results in .json format.
    
    Root is the root folder which contains experiment results     
    Destination is the folder name where the exported .json is put.
    It is found under the exports folder, which is in the parent folder of root
    """
    #root = r"C:\Local\siivonek\Data\eye_tracking_data\own_test_data\eyetrack_results"
    export_root = os.path.abspath( os.path.join(root, "..", "exports") )

    # Create exports directory if it doesn't exist
    if not os.path.exists(export_root):
        os.makedirs(export_root)


    # Iterate through all subjects and calibration videos
    # Save all error figures with outliers marked
    # Save all average errors for each calibration video

    folders = get_calibration_folders(root)

    # Errors in dictionary format
    error_summary = {}

    pp = pprint.PrettyPrinter(indent=2)

    for subject, calibs in folders.items():
        # Make export folder for subject
        subject_dir = os.path.join(export_root, subject)
        if not os.path.exists(subject_dir):
            os.makedirs(subject_dir)

        calibrations_path = os.path.join(root, subject, "calibrations")

        dict_data = {}
        # Holds the data for this calibration in dictionary format
        calibrations = {}

        # Iterate through last eight calibration videos
        # 1 - 3 first videos are the initial calibrations
        for calibration in calibs[-8:]:
            print("Processing " + subject + ": " + calibration)
            # Gaze error will be in format:
            # [clibration_point] [ error_x[], error_y[], error_combined[], outlier_indices[] ]
            gaze_error = get_calibration_error(calibrations_path, calibration)

            # Draw and save plots. Skip this step if plots exist
            filename = subject + "_" + calibration + ".png"
            filepath = os.path.join(subject_dir, filename)

            # Calibration point labels
            cp_names = [ "center",
                         "bottom_left",
                         "top_left",
                         "top_right",
                         "bottom_right" ]

            if not os.path.isfile(filepath):
                fig = plt.figure(figsize=(40, 20))
                labels = [['Center x',
                           'Bottom left x',
                           'Top left x',
                           'Top right x',
                           'Bottom right x'],
                          ['Center y',
                           'Bottom left y',
                           'Top left y',
                           'Top right y',
                           'Bottom right y']
                          ]
                # Separate the data for each point
                points = {}
                for i in range(5):
                    tmp = {}
                    filtered_x = []
                    filtered_y = []
                    #ax = fig.add_subplot(2, 5, i + 1)
                    ax_x = plt.subplot2grid((2, 5), (0, i))
                    ax_y = plt.subplot2grid((2, 5), (1, i))
                    ax_x.set_title(labels[0][i])
                    ax_y.set_title(labels[1][i])
                    ax_x.grid(color='lightgray', linestyle='--')
                    ax_y.grid(color='lightgray', linestyle='--')

                    t = range(0, len(gaze_error[i][2]))
                    color = []
                    for ii in range(len(gaze_error[i][2])):
                        if ii in gaze_error[i][3]:
                            # Outlier,
                            color.append('r')
                        else:
                            filtered_x.append(gaze_error[i][0][ii])
                            filtered_y.append(gaze_error[i][1][ii])
                            color.append('b')
                    tmp["x_error"] = filtered_x
                    tmp["x_stdev"] = np.std(filtered_x)
                    tmp["x_variance"] = np.var(filtered_x)
                    tmp["y_error"] = filtered_y
                    tmp["y_stdev"] = np.std(filtered_y)
                    tmp["y_variance"] = np.var(filtered_y)
                    # plt.scatter(range(0, len(gaze_error[i][0])), gaze_error[i][0])
                    # plt.scatter(range(0, len(gaze_error[i][1])), gaze_error[i][1])
                    ax_x.scatter(t, gaze_error[i][0], c=color)
                    ax_y.scatter(t, gaze_error[i][1], c=color)

                    points[cp_names[i]] = tmp

                calibrations[calibration] = points
                fig.savefig(filepath)
                plt.close(fig)

            # Calculate the x and y average error for each calibration point
            # Ignore outliers

            #point = 0
            average_x_errors = []
            average_y_errors = []
            for cp in gaze_error:
                error_avg_x = 0
                error_avg_y = 0
                error_sum_x = 0
                error_sum_y = 0
                length = len(cp[0])
                outliers = len(cp[3])
                # Check if x and y length is the same
                if ( length == len(cp[1])):
                    for i in range(length):
                        # Skip if index is marked as outlier
                        if not i in cp[3]:
                            error_sum_x += cp[0][i]
                            error_sum_y += cp[1][i]

                    if length > outliers:
                        error_avg_x = error_sum_x / (length-outliers)
                        error_avg_y = error_sum_y / (length-outliers)
                else:
                    print("Error, x and y dimension mismatch")

                average_x_errors.append(error_avg_x)
                average_y_errors.append(error_avg_y)

            # Save results for this calibration video into dictionary
            dict_data[calibration] = [average_x_errors, average_y_errors]

        error_summary[subject] = calibrations


            #plt.scatter(range(5), average_x_errors)
            #plt.scatter(range(5), average_y_errors)
            #plt.show()

        #pp.pprint(dict_data)

        #                                               0       1           2           3           4
        # Group error data by calibration point index (center, bottom left, top left, top right, bottom right)
        cp_x = []
        cp_y = []
        json_data_calib = {}
        # Initialize empty lists, one list for each calibration point
        # Ex. the center calibration point errors are all stored in the same list
        for i in range(5):
            cp_x.append([])
            cp_y.append([])

        for key, value in dict_data.items():
            for i in range(5):
                cp_x[i].append(value[0][i])
                cp_y[i].append(value[1][i])

            # Copy results into json format for output
            x_stdev = np.std(cp_x)
            y_stdev = np.std(cp_y)

            tmp = { "x_error": cp_x,
                    "y_error": cp_y,
                    "x_stdev": np.std(cp_x),
                    "y_stdev": np.std(cp_y),
                    "x_variance": np.var(cp_x),
                    "y_variance": np.var(cp_y)
            }
            json_data_calib[key] = tmp


        # Save plots. Skip this step if plot already exist
        filename = subject + "_error_summary.png"
        filepath = os.path.join(subject_dir, filename)
        #print(filepath)
        x = range(8)

        colors = ['k', 'red', 'orange', 'c', 'blue']
        #lines = ['k-', 'darkred-', 'salmon-', 'royalblue-', 'darkblue-']


        if not os.path.isfile(filepath):
            labels = ['Center',
                      'Bottom left',
                      'Top left',
                      'Top right',
                      'Bottom right']

            fig = plt.figure(figsize=(20, 20))
            # Plot structure:
            # Subplot 1 = x_error, 2 = y_error
            ax = fig.add_subplot(2, 1, 1)
            for i in range(5):
                ax.set_title("x-error")
                ax.grid(color='gray', linestyle='--', axis='y')
                ax.scatter(x, cp_x[i], c=colors[i], label=labels[i])
                m, b = np.polyfit(x, cp_x[i], 1)
                ax.plot(x, m*x+b, color=colors[i], linestyle='-')
                ax.legend(loc="upper left", bbox_to_anchor=(1,1))

            ax = fig.add_subplot(2, 1, 2)
            for i in range(5):
                ax.set_title("y-error")
                ax.grid(color='gray', linestyle='--', axis='y')
                ax.scatter(x, cp_y[i], c=colors[i], label=labels[i])
                m, b = np.polyfit(x, cp_y[i], 1)
                ax.plot(x, m * x + b, color=colors[i], linestyle='-')
                ax.legend(loc="upper left", bbox_to_anchor=(1, 1))


            fig.savefig(filepath)
            plt.close(fig)

        # Save summary in dictionary format
        #error_summary[subject] = json_data_calib

    # Dump error summaries in JSON format
    with open(os.path.join(destination, "error_summary.json"), 'w') as file:
        print("Dumping data in JSON format. Path: " + destination)
        json.dump(error_summary, file)
        file.close()


if __name__ == "__main__":
    # Check command line arguments
    if len(sys.argv) < 3:
        print("Need at least two arguments: data root folder and destination folder")
    else:
        visualize_error(sys.argv[1], sys.argv[2])
