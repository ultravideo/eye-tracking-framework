# Visualize gaze point error compared to calibration point

import os.path
import matplotlib.pyplot as plt
import json
import pprint
import numpy as np

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

pp = pprint.PrettyPrinter(indent=2)

for subject, calibs in folders.items():
    print("Processing " + subject)

    calibrations_path = os.path.join(root, subject, "calibrations")

    # Iterate through last eight calibration videos
    # 1 - 3 first videos are the initial calibrations
    dict_data = {}
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

    # Order error data by calibration point
    cp0_x = []
    cp1_x = []
    cp2_x = []
    cp3_x = []
    cp4_x = []
    cp0_y = []
    cp1_y = []
    cp2_y = []
    cp3_y = []
    cp4_y = []
    for key, value in dict_data.items():
        cp0_x.append(value[0][0])
        cp1_x.append(value[0][1])
        cp2_x.append(value[0][2])
        cp3_x.append(value[0][3])
        cp4_x.append(value[0][4])
        cp0_y.append(value[1][0])
        cp1_y.append(value[1][1])
        cp2_y.append(value[1][2])
        cp3_y.append(value[1][3])
        cp4_y.append(value[1][4])

    #pp.pprint(cp0)


    # Save plots. Skip this step if plot already exist
    filename = subject + "_error_summary.png"
    filepath = os.path.join(export_root, filename)
    #print(filepath)
    x = range(8)
    if not os.path.isfile(filepath):
        plt.figure(figsize=(20, 10))

        # Plot structure:
        # Subplot 1 = x_error, 2 = y_error

        plt.subplot(2, 1, 1)
        plt.scatter(x, cp0_x, c='b', label='Center')
        m, b = np.polyfit(x, cp0_x, 1)
        plt.plot(x, m*x+b, 'b-')
        plt.scatter(x, cp1_x, c='r', label='Bottom left')
        m, b = np.polyfit(x, cp1_x, 1)
        plt.plot(x, m * x + b, 'r-')
        plt.scatter(x, cp2_x, c='g', label='Top left')
        m, b = np.polyfit(x, cp2_x, 1)
        plt.plot(x, m * x + b, 'g-')
        plt.scatter(x, cp3_x, c='y', label='Top right')
        m, b = np.polyfit(x, cp3_x, 1)
        plt.plot(x, m * x + b, 'y-')
        plt.scatter(x, cp4_x, c='c', label='Bottom right')
        m, b = np.polyfit(x, cp4_x, 1)
        plt.plot(x, m * x + b, 'c-')

        plt.subplot(2, 1, 2)
        plt.scatter(x, cp0_y, c='b', label='Center')
        m, b = np.polyfit(x, cp0_y, 1)
        plt.plot(x, m * x + b, 'b-')
        plt.scatter(x, cp1_y, c='r', label='Bottom left')
        m, b = np.polyfit(x, cp1_y, 1)
        plt.plot(x, m * x + b, 'r-')
        plt.scatter(x, cp2_y, c='g', label='Top left')
        m, b = np.polyfit(x, cp2_y, 1)
        plt.plot(x, m * x + b, 'g-')
        plt.scatter(x, cp3_y, c='y', label='Top right')
        m, b = np.polyfit(x, cp3_y, 1)
        plt.plot(x, m * x + b, 'y-')
        plt.scatter(x, cp4_y, c='c', label='Bottom right')
        m, b = np.polyfit(x, cp4_y, 1)
        plt.plot(x, m * x + b, 'c-')

        plt.legend(loc="upper left", bbox_to_anchor=(1,1))

        plt.savefig(filepath)
        plt.clf()

    # Save summary in dictionary format
    #error_summary[subject] = dict_data

# Dump error summaries in JSON format
#with open(os.path.join(export_root, "error_summary.json"), 'w') as file:
    #json.dump(error_summary, file)
    #file.close()







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


