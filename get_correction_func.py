import os
import cv2
import numpy as np
from get_calibration_error import get_calibration_error
from get_video_order import get_video_order

import pprint

TEST_VIDEO_FOLDER = r"D:\Raw_Files\eye_tracking_final_sequences_y4m"
CP_NAMES = ["center",
            "bottom_left",
            "top_left",
            "top_right",
            "bottom_right"]

CP_LOCATIONS = [
        [0.5, 0.5],  # Center
        [114 / 384, 1 / 3],  # Down left
        [114 / 384, 2 / 3],  # Up left
        [270 / 384, 2 / 3],  # Up right
        [270 / 384, 1 / 3]]  # Down right


def get_cp_averages(subject):
    calibrations_path = os.path.join(subject, "calibrations")

    average_dict = {}

    # Get calibration directories

    # Check if directory contains calibrations
    if os.path.isdir(calibrations_path):
        calibrations = next(os.walk(calibrations_path))[1]
    else:
        calibrations = []

    # Iterate through last eight entries. First 1-3 folders can be initial calibrations
    for calibration in calibrations[-8:]:
        avg_tmp = {}
        # Gaze error will be in format:
        # { calibration_point: [ error_x[], error_y[], error_combined[], outlier_indices[] ] }
        # Fixation error will be in format:
        # { calibration_point: [ start frame, end frame, error x, error y, cp start frame, cp end frame ] }
        gaze_error, fixation_error = get_calibration_error(calibrations_path, calibration)

        # Fixation error won't be used

        # Calculate averages for raw gaze points
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
                    # Flip y to negative, since in OpenCV y-is positive downwards
                    error_avg_y = -(error_sum_y / (length - outliers))
            else:
                print("Error, x and y dimension mismatch")

            gaze_tmp[cp] = [error_avg_x, error_avg_y]

        avg_tmp['gaze_error'] = gaze_tmp

        average_dict[calibration] = avg_tmp

    return average_dict


def get_frame_count(video):
    video_file_path = os.path.join(TEST_VIDEO_FOLDER, video)
    handle = cv2.VideoCapture(video_file_path)
    count = int(handle.get(cv2.CAP_PROP_FRAME_COUNT))

    return count


def get_fps(video):
    # FPS is included in every video name. Split and retrieve
    # Format: name_resolution_fps.
    substr = video.split('_')
    if len(substr[2]) > 2:
        fps = int(substr[2][:2])
    else:
        fps = int(substr[2])

    return fps


def get_calibration_folders(subject):
    calibrations_path = os.path.join(subject, "calibrations")

    # Get calibration directories
    if os.path.isdir(calibrations_path):
        calibrations = next(os.walk(calibrations_path))[1]
    else:
        calibrations = []

    # Only last 8 are relevant
    return calibrations[-8:]


def get_timeline(subject):
    order = get_video_order(subject)

    calibrations = get_calibration_folders(subject)

    # Construct time line. Insert calibrations into timeline after every 4 normal videos
    # Calibrations last around 10 seconds average
    calibration_time = 10.0
    timeline = []
    insert_calibration = 0
    calibration = 0
    for i in range(len(order)):
        tmp = {}
        if insert_calibration == 4:
            tmp['name'] = calibrations[calibration]
            tmp['frame_count'] = 0
            tmp['fps'] = 0
            tmp['length'] = calibration_time
            calibration += 1
            insert_calibration = 0
        else:
            tmp['name'] = order[i]
            tmp['frame_count'] = get_frame_count(order[i])
            tmp['fps'] = get_fps(order[i])
            tmp['length'] = tmp['frame_count'] / tmp['fps']
            insert_calibration += 1

        timeline.append(tmp)

    # Purkkafix9000
    # One video has wrong fps in it's filename. Fix here
    for item in timeline:
        if item['name'] == "oldTownCross_1920x1080_60.y4m":
            item['fps'] = 50
            item['length'] = item['frame_count'] / item['fps']
            break

    for item in timeline:
        if item['name'] == "rushHour_1920x1080_50.y4m":
            item['fps'] = 25
            item['length'] = item['frame_count'] / item['fps']
            break

    return timeline


def order_by_cp(average_data):
    """
    Group average data by calibration point. Previously, data is grouped by calibration video
    """
    cp_x = []
    cp_y = []

    # Initialize empty lists for re-arranging average values
    # Ex. the center calibration point errors are all stored in the same list index
    for i in range(5):
        cp_x.append([])
        cp_y.append([])

    for calibration, values in average_data.items():
        for i in range(5):
            cp_x[i].append(values['gaze_error'][CP_NAMES[i]][0])
            cp_y[i].append(values['gaze_error'][CP_NAMES[i]][1])

    output = {}
    for i in range(5):
        output[CP_NAMES[i]] = [cp_x[i], cp_y[i]]

    return output


def get_video_start_time(timeline, video):
    time = 0
    for item in timeline:
        if item['name'] == video:
            break
        time += item['length']

    return time


def get_video_end_time(timeline, video):
    time = 0
    found = False
    for item in timeline:
        if item['name'] == video:
            found = True
        time += item['length']
        if found:
            break

    return time


def get_transform_matrix_at_time(video, timeline, linefits):
    # Use the estimated average position of the five calibration points to calculate
    # perspective transform matrix

    # Get time from middle of video
    time = (get_video_start_time(timeline, video) + get_video_end_time(timeline, video)) / 2

    tmp = []
    for i in range(1, 5):
        m = linefits[CP_NAMES[i]]['x'][0]
        b = linefits[CP_NAMES[i]]['x'][1]
        x_pos = m * time + b
        m = linefits[CP_NAMES[i]]['y'][0]
        b = linefits[CP_NAMES[i]]['y'][1]
        y_pos = m * time + b
        tmp.append([CP_LOCATIONS[i][0] + x_pos, CP_LOCATIONS[i][1] + y_pos])

    # Note: in OpenCV, y is positive downwards
    # In Pupil Labs software, y is positive upwards
    pts1 = np.float32(tmp)
    pts2 = np.float32([CP_LOCATIONS[1], CP_LOCATIONS[2], CP_LOCATIONS[3], CP_LOCATIONS[4]])

    return cv2.getPerspectiveTransform(pts1, pts2)


def get_correction_func(subject, video):
    """
    Get the gaze point correction function for given subject.
    
    subject is the root folder which contains the video data for said subject 
    """

    # Parse test videos to get the test time line.
    #  and line fits for error evolution of x and y error for the duration of the test

    average_gaze_data = get_cp_averages(subject)
    cp_ordered_data = order_by_cp(average_gaze_data)
    timeline = get_timeline(subject)
    calibrations = get_calibration_folders(subject)

    # Get x axis values for line fitting
    x = []
    for i in range(len(calibrations)):
        x.append(get_video_start_time(timeline, calibrations[i]))

    # Calculate line fits for each calibration point
    linefits = {}
    for i in range(1, 5):
        tmp = {}
        m, b = np.polyfit(x, cp_ordered_data[CP_NAMES[i]][0], 1)
        tmp['x'] = [m, b]
        m, b = np.polyfit(x, cp_ordered_data[CP_NAMES[i]][1], 1)
        tmp['y'] = [m, b]
        linefits[CP_NAMES[i]] = tmp

    M = get_transform_matrix_at_time(video, timeline, linefits)

    def correct_coordinates(x, y):
        tmp = np.float32([[[x, y]]])
        corr_tmp = cv2.perspectiveTransform(tmp, M)
        return corr_tmp[0, 0]

    return correct_coordinates


if __name__ == "__main__":
    func = get_correction_func(r"C:\Local\siivonek\Data\eye_tracking_data\own_test_data\eyetrack_results\23-f-25")


