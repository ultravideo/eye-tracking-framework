# Visualize gaze point error compared to calibration point

import os.path
import matplotlib.pyplot as plt
import json
import pprint
import numpy as np

from get_calibration_error import get_calibration_error
from get_calibration_folders import get_calibration_folders

root = r"C:\Local\siivonek\Data\eye_tracking_data\own_test_data\eyetrack_results"
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

# Calibration point lables
labels = [ 'Center',
           'Bottom left',
           'Top left',
           'Top right',
           'Bottom right']

for subject, calibs in folders.items():
    # Make export folder for subject
    subject_dir = os.path.join(export_root, subject)
    if not os.path.exists(subject_dir):
        os.makedirs(subject_dir)

    calibrations_path = os.path.join(root, subject, "calibrations")

    # Iterate through last eight calibration videos
    # 1 - 3 first videos are the initial calibrations
    dict_data = {}
    for calibration in calibs[-8:]:
        print("Processing " + subject + ": " + calibration)
        # Gaze error will be in format:
        # [clibration_point] [ error_x[], error_y[], error_combined[], outlier_indices[] ]
        gaze_error = get_calibration_error(calibrations_path, calibration)

        # Draw and save plots. Skip this step if plots exist
        filename = subject + "_" + calibration + ".png"
        filepath = os.path.join(subject_dir, filename)


        if not os.path.isfile(filepath):
            fig = plt.figure(figsize=(20, 10))

            for i in range(5):
                ax = fig.add_subplot(2, 3, i + 1)
                ax.set_title(labels[i])
                ax.grid(color='lightgray', linestyle='--')

                t = range(0, len(gaze_error[i][2]))
                color = []
                for ii in range(len(gaze_error[i][2])):
                    if ii in gaze_error[i][3]:
                        color.append('r')
                    else:
                        color.append('b')
                # plt.scatter(range(0, len(gaze_error[i][0])), gaze_error[i][0])
                # plt.scatter(range(0, len(gaze_error[i][1])), gaze_error[i][1])
                ax.scatter(t, gaze_error[i][2], c=color)

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

                error_avg_x = error_sum_x / (length-outliers)
                error_avg_y = error_sum_y / (length-outliers)
            else:
                print("Error, x and y dimension mismatch")

            average_x_errors.append(error_avg_x)
            average_y_errors.append(error_avg_y)

        # Save results for this calibration video into dictionary
        dict_data[calibration] = [average_x_errors, average_y_errors]


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
        json_data_calib[key] = [cp_x, cp_y]


    # Save plots. Skip this step if plot already exist
    filename = subject + "_error_summary.png"
    filepath = os.path.join(subject_dir, filename)
    #print(filepath)
    x = range(8)

    colors = ['k', 'red', 'orange', 'c', 'blue']
    #lines = ['k-', 'darkred-', 'salmon-', 'royalblue-', 'darkblue-']


    if not os.path.isfile(filepath):
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
    error_summary[subject] = json_data_calib

# Dump error summaries in JSON format
with open(os.path.join(export_root, "error_summary.json"), 'w') as file:
    print("Dumping data in JSON format")
    json.dump(error_summary, file)
    file.close()

