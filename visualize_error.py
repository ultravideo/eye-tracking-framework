# Visualize gaze point error compared to calibration point

import os.path
import matplotlib.pyplot as plt
import json

from get_calibration_error import get_calibration_error
from get_calibration_folders import get_calibration_folders

root = r"C:\Local\siivonek\Data\eye_tracking_data\own_test_data\eyetrack_results"
export_root = r"C:\Local\siivonek\Data\eye_tracking_data\own_test_data\exports"

# Iterate through all subjects and calibration videos
# Save all error figures with outliers marked
# Save all average errors for each calibration video

folders = get_calibration_folders(root)

# Errors in dictionary format
error_summary = {}

for subject, calibs in folders.items():
    print("Processing " + subject)

    calibrations_path = os.path.join(root, subject, "calibrations")


    # Iterate through last eight calibration videos
    # 1 - 3 first videos are the initial calibrations
    calibration_avg_x_errors = []
    calibration_avg_y_errors = []
    dict_data = []
    for calibration in calibs[-8:]:
        # Gaze error will be in format:
        # [clibration_point] [ error_x[], error_y[], error_combined[], outlier_indices[] ]
        gaze_error = get_calibration_error(calibrations_path, calibration)

        # Draw and save plots. Skip this step if plots exist
        filename = subject + "_" + calibration + ".png"
        filepath = os.path.join(export_root, filename)
        if not os.path.isfile(filepath):
            for i in range(5):
                plt.subplot(2, 3, i + 1)
                t = range(0, len(gaze_error[i][2]))
                color = []
                for ii in range(len(gaze_error[i][2])):
                    if ii in gaze_error[i][3]:
                        color.append('r')
                    else:
                        color.append('b')
                # plt.scatter(range(0, len(gaze_error[i][0])), gaze_error[i][0])
                # plt.scatter(range(0, len(gaze_error[i][1])), gaze_error[i][1])
                plt.scatter(t, gaze_error[i][2], c=color)

            plt.savefig(filepath)
            plt.clf()

        # Calculate the x and y average error for each calibration point
        # Ignore outliers

        #point = 0
        average_x_errors = []
        average_y_errors = []

        # Averages over all points
        total_avg_x_error = 0
        total_avg_y_error = 0
        total_sum_x = 0
        total_sum_y = 0
        total_length = 0

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

                        total_sum_x += cp[0][i]
                        total_sum_y += cp[1][i]
                        total_length += 1
                error_avg_x = error_sum_x / (length-outliers)
                error_avg_y = error_sum_y / (length-outliers)
            else:
                print("Error, x and y dimension mismatch")

            average_x_errors.append(error_avg_x)
            average_y_errors.append(error_avg_y)


        total_avg_x_error = total_sum_x / total_length
        total_avg_y_error = total_sum_y / total_length
        calibration_avg_x_errors.append(total_avg_x_error)
        calibration_avg_y_errors.append(total_avg_y_error)
        dict_data.append([total_avg_x_error, total_avg_y_error])

    # Save plots. Skip this step if plot already exist
    filename = subject + "_error_summary.png"
    filepath = os.path.join(export_root, filename)
    #print(filepath)
    if not os.path.isfile(filepath):
        plt.scatter(range(8), calibration_avg_x_errors, c='b')
        plt.scatter(range(8), calibration_avg_y_errors, c='r')
        plt.savefig(filepath)
        plt.clf()

    # Save summary in dictionary format
    error_summary[subject] = dict_data
        #plt.scatter(range(5), average_x_errors)
        #plt.scatter(range(5), average_y_errors)
        #plt.show()
            #print("Calibration point " + str(point))
            #print("Error avg x " + str(error_avg_x) + ", y " + str(error_avg_y))
            #point += 1

# Dump error summaries in JSON format
with open(os.path.join(export_root, "error_summary.json"), 'w') as file:
    json.dump(error_summary, file)
    file.close()







#test = r"C:\Local\siivonek\Data\eye_tracking_data\own_test_data\eyetrack_results\22-f-25\calibrations"

#gaze_error = get_calibration_error(test, "003")


"""
for i in range(5):
    plt.subplot(2, 3, i+1)
    t = range(0, len(gaze_error[i][2]))
    color = []
    for ii in range(len(gaze_error[i][2])):
        if ii in gaze_error[i][3]:
            color.append('r')
        else:
            color.append('b')
    #plt.scatter(range(0, len(gaze_error[i][0])), gaze_error[i][0])
    #plt.scatter(range(0, len(gaze_error[i][1])), gaze_error[i][1])
    plt.scatter(t, gaze_error[i][2], c = color)
    #plt.scatter(range(0, len(gaze_error[i][0])), gaze_error[i][0])
    #plt.scatter(range(0, len(gaze_error[i][1])), gaze_error[i][1])

plt.show()
"""


