import os.path
import matplotlib.pyplot as plt
import json
import numpy as np
import sys

from get_calibration_error import get_calibration_error
from get_calibration_folders import get_calibration_folders
from gather_and_process import gather_and_process

X_WIDTH = 3840
Y_HEIGHT = 2160


def visualize_error(root, destination):
    """    
    Draws plots for data and writes results in .json format.
    
    Root is the root folder which contains experiment results     
    Destination is the folder name where the exported subject folders with the plots are put
    It is found under the exports folder, which is in the parent folder of root
    """

    export_root = os.path.abspath(os.path.join(root, "..", "exports"))

    # Create exports directory if it doesn't exist
    if not os.path.exists(export_root):
        os.makedirs(export_root)

    # Load data
    datafile = os.path.join(export_root, destination, "processed_gaze_points.json")
    average_file = os.path.join(export_root, destination, "processed_averages.json")

    if not os.path.isfile(datafile) or not os.path.isfile(average_file):
        print("Processed data not found. Gather and process")
        gather_and_process(root, destination)

    with open(datafile) as file:
        data = json.load(file)
        file.close()

    with open(average_file) as file:
        avg_data = json.load(file)
        file.close()

    # Iterate through all subjects and calibration videos
    # Save all error figures with outliers marked
    # Save all average errors for each calibration video

    for subject, calibs in data.items():
        # Make export folder for subject
        subject_dir = os.path.join(export_root, destination, subject)
        if not os.path.exists(subject_dir):
            os.makedirs(subject_dir)

        for calibration in calibs:
            print("Processing " + subject + ": " + calibration)
            # Gaze error will be in format:
            # { calibration_point: [ error_x[], error_y[], error_combined[], outlier_indices[] }
            gaze_error = data[subject][calibration]['gaze_error']
            # Fixation error will be in format:
            # { calibration_point: [ start frame, end frame, error x, error y, cp start frame, cp end frame ] }
            fixation_error = data[subject][calibration]['fixation_error']

            # Draw and save plots. Skip this step if plots exist
            filename = subject + "_" + calibration + ".png"
            filepath = os.path.join(subject_dir, filename)

            # Calibration point labels
            cp_names = ["center",
                        "bottom_left",
                        "top_left",
                        "top_right",
                        "bottom_right"]

            # Skip if file already exist
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
                    # Values as pixels
                    pxl_x = []
                    pxl_y = []

                    ax_x = plt.subplot2grid((3, 5), (0, i))
                    ax_y = plt.subplot2grid((3, 5), (1, i))
                    ax_xy = plt.subplot2grid((3, 5), (2, i))
                    ax_x.set_title(labels[0][i])
                    ax_y.set_title(labels[1][i])
                    ax_xy.set_title(cp_names[i])

                    ax_x.grid(color='lightgray', linestyle='--')
                    ax_y.grid(color='lightgray', linestyle='--')
                    ax_xy.grid(color='lightgray', linestyle='--')

                    t = range(0, len(gaze_error[cp_names[i]][2]))
                    color = []
                    for ii in range(len(gaze_error[cp_names[i]][2])):
                        if ii in gaze_error[cp_names[i]][3]:
                            # Outlier
                            color.append('r')
                        else:
                            filtered_x.append(gaze_error[cp_names[i]][0][ii])
                            pxl_x.append(gaze_error[cp_names[i]][0][ii] * X_WIDTH)
                            filtered_y.append(gaze_error[cp_names[i]][1][ii])
                            pxl_y.append(gaze_error[cp_names[i]][1][ii] * Y_HEIGHT)
                            color.append('b')
                    tmp["x_error"] = filtered_x
                    tmp["x_error_pxl"] = pxl_x
                    tmp["x_stdev"] = np.std(filtered_x)
                    tmp["x_variance"] = np.var(filtered_x)
                    tmp["y_error"] = filtered_y
                    tmp["y_error_pxl"] = pxl_y
                    tmp["y_stdev"] = np.std(filtered_y)
                    tmp["y_variance"] = np.var(filtered_y)

                    # plt.scatter(range(0, len(gaze_error[i][0])), gaze_error[i][0])
                    # plt.scatter(range(0, len(gaze_error[i][1])), gaze_error[i][1])
                    # Convert to pixel values
                    pxl_x_tmp = []
                    pxl_y_tmp = []

                    for val in gaze_error[cp_names[i]][0]:
                        pxl_x_tmp.append(val * X_WIDTH)
                    for val in gaze_error[cp_names[i]][1]:
                        pxl_y_tmp.append(val * Y_HEIGHT)

                    margin = 10
                    # Set axis limits
                    x_lim = 0
                    if len(tmp['x_error_pxl']) > 0:
                        if abs(min(tmp['x_error_pxl'])) > abs(max(tmp['x_error_pxl'])):
                            x_lim = abs(min(tmp['x_error_pxl'])) + margin
                        else:
                            x_lim = abs(max(tmp['x_error_pxl'])) + margin
                    if len(tmp['y_error_pxl']) > 0:
                        if abs(min(tmp['y_error_pxl'])) > abs(max(tmp['y_error_pxl'])):
                            y_lim = abs(min(tmp['y_error_pxl'])) + margin
                        else:
                            y_lim = abs(max(tmp['y_error_pxl'])) + margin

                    ax_xy.set_xlim(-x_lim, x_lim)
                    ax_xy.set_ylim(-y_lim, y_lim)
                    ax_xy.spines['left'].set_position('center')
                    ax_xy.spines['right'].set_color(None)
                    ax_xy.spines['bottom'].set_position('center')
                    ax_xy.spines['top'].set_color(None)

                    ax_x.scatter(t, pxl_x_tmp, c=color, marker='.')
                    ax_y.scatter(t, pxl_y_tmp, c=color, marker='.')
                    ax_xy.scatter(tmp['x_error_pxl'], tmp['y_error_pxl'], marker='.')

                    # Draw fixations if exists
                    if len(fixation_error[cp_names[i]]) > 0:
                        for row in fixation_error[cp_names[i]]:
                            # Correct fixation start and end frames
                            # indexes:  0 = fixation start frame
                            #           1 = fixation end frame
                            #           2 = fixation error x
                            #           3 = fixation error y
                            #           4 = calibration point start frame
                            #           5 = calibration point end frame
                            fixation_t = [row[0] - row[4], row[1] - row[4]]
                            fixation_x = [row[2] * X_WIDTH, row[2] * X_WIDTH]
                            fixation_y = [row[3] * Y_HEIGHT, row[3] * Y_HEIGHT]

                            ax_x.plot(fixation_t, fixation_x, '-k')
                            ax_y.plot(fixation_t, fixation_y, '-k')

                    points[cp_names[i]] = tmp

                fig.savefig(filepath)
                plt.close(fig)

        #                                               0       1           2           3           4
        # Group error data by calibration point index (center, bottom left, top left, top right, bottom right)
        cp_x = []
        cp_y = []
        fixation_cp_x = []
        fixation_cp_y = []
        json_data_calib = {}
        # Initialize empty lists for re-arranging average values
        # Ex. the center calibration point errors are all stored in the same list index
        for i in range(5):
            cp_x.append([])
            cp_y.append([])
            fixation_cp_x.append([])
            fixation_cp_y.append([])

        for calibration, values in avg_data[subject].items():
            for i in range(5):
                cp_x[i].append(values['gaze_error'][cp_names[i]][2])
                cp_y[i].append(values['gaze_error'][cp_names[i]][3])
                if values['fixation_error'][cp_names[i]]:
                    fixation_cp_x[i].append(values['fixation_error'][cp_names[i]][2])
                    fixation_cp_y[i].append(values['fixation_error'][cp_names[i]][3])
                else:
                    fixation_cp_x[i].append(float('nan'))
                    fixation_cp_y[i].append(float('nan'))
            # Copy results into json format for output
            tmp = {"x_error": cp_x,
                   "y_error": cp_y,
                   "x_stdev": np.std(cp_x),
                   "y_stdev": np.std(cp_y),
                   "x_variance": np.var(cp_x),
                   "y_variance": np.var(cp_y)
                   }
            json_data_calib[calibration] = tmp

        # Save plots. Skip this step if plot already exist
        filename = subject + "_error_summary.png"
        filepath = os.path.join(subject_dir, filename)
        # print(filepath)
        x = np.array(range(8))

        colors = ['k', 'red', 'orange', 'c', 'blue']
        # lines = ['k-', 'darkred-', 'salmon-', 'royalblue-', 'darkblue-']

        labels = ['Center',
                  'Bottom left',
                  'Top left',
                  'Top right',
                  'Bottom right']

        if not os.path.isfile(filepath):
            fig = plt.figure(figsize=(20, 20))

            ax = plt.subplot2grid((2, 1), (0, 0))
            ax.set_title("x-error")
            ax.grid(color='gray', linestyle='--', axis='y')
            for i in range(5):
                ax.scatter(x, cp_x[i], c=colors[i], label=labels[i])
                m, b = np.polyfit(x, cp_x[i], 1)
                ax.plot(x, m * x + b, color=colors[i], linestyle='-')
            ax.legend(loc="upper left", bbox_to_anchor=(1, 1))

            # ax = fig.add_subplot(2, 1, 2)
            ax = plt.subplot2grid((2, 1), (1, 0))
            ax.set_title("y-error")
            ax.grid(color='gray', linestyle='--', axis='y')
            for i in range(5):
                ax.scatter(x, cp_y[i], c=colors[i], label=labels[i])
                m, b = np.polyfit(x, cp_y[i], 1)
                ax.plot(x, m * x + b, color=colors[i], linestyle='-')
            ax.legend(loc="upper left", bbox_to_anchor=(1, 1))

            fig.savefig(filepath)
            plt.close(fig)

        # Save different version of summary

        filename = subject + "_error_summary_xy.png"
        filepath = os.path.join(subject_dir, filename)

        if not os.path.isfile(filepath):
            fig = plt.figure(figsize=(20, 20))
            ax = plt.subplot2grid((1, 1), (0, 0))
            ax.spines['left'].set_position('zero')
            ax.spines['right'].set_color(None)
            ax.spines['bottom'].set_position('zero')
            ax.spines['top'].set_color(None)
            ax.grid(color='lightgray', linestyle='--')

            for i in range(5):
                ax.plot(cp_x[i], cp_y[i], c=colors[i], linestyle='--', marker='o', label=labels[i])
            ax.legend(loc="upper left", bbox_to_anchor=(1, 1))

            fig.savefig(filepath)
            plt.close(fig)

        # Save summaries using fixation data instead of raw gaze point data

        filename = subject + "_error_summary_fixation.png"
        filepath = os.path.join(subject_dir, filename)

        if not os.path.isfile(filepath):
            fig = plt.figure(figsize=(20, 20))
            ax = plt.subplot2grid((2, 1), (0, 0))
            ax.set_title("x-error")
            ax.grid(color='gray', linestyle='--', axis='y')
            for i in range(5):
                # Numpy polyfit cannot handle NaNs -> clean the data before polyfit
                # Also, convert to numpy array so clean indexes work
                clean_x = np.isfinite(fixation_cp_x[i])
                tmp_x = np.array(fixation_cp_x[i])
                ax.scatter(x, fixation_cp_x[i], c=colors[i], label=labels[i])
                # Need at least two valid points
                if not len(tmp_x[clean_x]) < 2:
                    m, b = np.polyfit(x[clean_x], tmp_x[clean_x], 1)
                    ax.plot(x, m * x + b, color=colors[i], linestyle='-')
            ax.legend(loc="upper left", bbox_to_anchor=(1, 1))

            ax = plt.subplot2grid((2, 1), (1, 0))
            ax.set_title("y-error")
            ax.grid(color='gray', linestyle='--', axis='y')
            for i in range(5):
                clean_y = np.isfinite(fixation_cp_y[i])
                tmp_y = np.array(fixation_cp_y[i])
                ax.scatter(x, fixation_cp_y[i], c=colors[i], label=labels[i])
                # Need at least two valid points
                if not len(tmp_y[clean_y]) < 2:
                    m, b = np.polyfit(x[clean_y], tmp_y[clean_y], 1)
                    ax.plot(x, m * x + b, color=colors[i], linestyle='-')
            ax.legend(loc="upper left", bbox_to_anchor=(1, 1))

            fig.savefig(filepath)
            plt.close(fig)

        filename = subject + "_error_summary_xy_fixation.png"
        filepath = os.path.join(subject_dir, filename)

        if not os.path.isfile(filepath):
            fig = plt.figure(figsize=(20, 20))
            ax = plt.subplot2grid((1, 1), (0, 0))
            ax.spines['left'].set_position('zero')
            ax.spines['right'].set_color(None)
            ax.spines['bottom'].set_position('zero')
            ax.spines['top'].set_color(None)
            ax.grid(color='lightgray', linestyle='--')

            for i in range(5):
                ax.plot(fixation_cp_x[i], fixation_cp_y[i], c=colors[i], linestyle='--', marker='o', label=labels[i])
            ax.legend(loc="upper left", bbox_to_anchor=(1, 1))

            fig.savefig(filepath)
            plt.close(fig)

if __name__ == "__main__":
    # Check command line arguments
    if len(sys.argv) < 3:
        print("Need at least two arguments: data root folder and destination folder")
    else:
        visualize_error(sys.argv[1], sys.argv[2])
