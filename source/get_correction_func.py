import os
import cv2
import numpy as np

from sklearn.cluster import KMeans
from sklearn import metrics

import config as cfg
from get_calibration_error import get_calibration_error
from get_video_order import get_video_order


def choose_cluster(data, labels, n_clusters):
    # Choose best cluster based on cluster size
    clusters = {}

    best_score = 0
    best_cluster = 0

    for cluster in range(n_clusters):
        clusters[cluster] = np.array([x[0] for x in zip(data, labels) if x[1] == cluster])

        if best_score < len(clusters[cluster]):
            best_score = len(clusters[cluster])
            best_cluster = cluster

    return clusters[best_cluster]


def cluster_analysis(data):
    # Cluster gaze points if they are dispersed.
    # Return best cluster, other clusters are pruned out
    avg = np.average(data, axis=0)

    x_low = avg[0] - cfg.CLUSTER_THRESHOLD_WIDTH / 2
    x_high = avg[0] + cfg.CLUSTER_THRESHOLD_WIDTH / 2
    y_low = avg[1] - cfg.CLUSTER_THRESHOLD_HEIGHT / 2
    y_high = avg[1] + cfg.CLUSTER_THRESHOLD_HEIGHT / 2
    in_threshold = 0
    # Check percentage of gaze points within threshold
    for i in data:
        if not (i[0] < x_low or i[0] > x_high or i[1] < y_low or i[1] > y_high):
            in_threshold += 1

    if in_threshold / len(data) < cfg.CLUSTER_PERCENTAGE_THRESHOLD:
        # Perform clustering
        # Decide optimal number of clusters with silhouette method. Try with cluster num between 2 to max clusters
        tmp = {}  # Store clustering scores here
        c_labels = {}
        for n_clusters in range(2, cfg.MAX_CLUSTERS + 1):
            # Initialize clustering with n clusters and a random state for consistent results
            cluster_func = KMeans(n_clusters=n_clusters, random_state=1)
            c_labels[n_clusters] = cluster_func.fit_predict(data)

            # The average silhouette score for n clusters
            silhouette_avg = metrics.silhouette_score(data, c_labels[n_clusters])

            tmp[n_clusters] = silhouette_avg

        optimal_n = max(tmp.items(), key=lambda x: x[1])
        output = choose_cluster(data, c_labels[optimal_n[0]], optimal_n[0])

    else:
        output = data

    return output


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
            print("Processing: ", os.path.basename(os.path.normpath(subject)), calibration, cp)

            x = [x for index, x in enumerate(values[0]) if index not in values[3]]
            y = [y for index, y in enumerate(values[1]) if index not in values[3]]

            # Cluster analysis
            # Perform clustering if gaze points are dispersed.
            # After clustering, select the best cluster for subsequent processing
            tmp_data = np.column_stack((x, y))
            if len(tmp_data) > 0:
                clustered_data = cluster_analysis(tmp_data)

                error_avg_x = np.average(clustered_data[:, 0])
                error_avg_y = np.average(clustered_data[:, 1])

                gaze_tmp[cp] = [error_avg_x, error_avg_y]
            else:
                gaze_tmp[cp] = []

        avg_tmp['gaze_error'] = gaze_tmp

        average_dict[calibration] = avg_tmp

    return average_dict


def get_frame_count(video):
    video_file_path = os.path.join(cfg.TEST_VIDEO_FOLDER, video)
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

    # Construct time line. Insert calibrations into timeline after every 5 normal videos
    timeline = []
    insert_calibration = 0
    calibration = 0
    for i in range(len(order)):
        tmp = {}
        if insert_calibration == 4:
            tmp['name'] = calibrations[calibration]
            tmp['frame_count'] = 0
            tmp['fps'] = 0
            tmp['length'] = cfg.CALIBRATION_CHECK_TIME
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
            cp_x[i].append(values['gaze_error'][cfg.CALIBRATION_POINT_NAMES[i]][0])
            cp_y[i].append(values['gaze_error'][cfg.CALIBRATION_POINT_NAMES[i]][1])

    output = {}
    for i in range(5):
        output[cfg.CALIBRATION_POINT_NAMES[i]] = [cp_x[i], cp_y[i]]

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


def get_correction_func_dispenser(subject):
    """
    Get the gaze point correction function for given subject.
    
    subject is the root folder which contains the video data for said subject 
    """

    average_gaze_data = get_cp_averages(subject)
    cp_ordered_data = order_by_cp(average_gaze_data)
    timeline = get_timeline(subject)
    calibrations = get_calibration_folders(subject)

    # Get x axis values for line fitting
    x_tmp = []
    for i in range(len(calibrations)):
        x_tmp.append(get_video_start_time(timeline, calibrations[i]))

    x = np.array(x_tmp)

    # Calculate line fits for each calibration point
    linefits = {}

    for i in range(1, 5):
        tmp = {}

        m, b = np.polyfit(x, cp_ordered_data[cfg.CALIBRATION_POINT_NAMES[i]][0], 1)
        tmp['x'] = [m, b]

        m, b = np.polyfit(x, cp_ordered_data[cfg.CALIBRATION_POINT_NAMES[i]][1], 1)
        tmp['y'] = [m, b]

        linefits[cfg.CALIBRATION_POINT_NAMES[i]] = tmp

    def get_transform_matrix_at_time(video):
        # Use the estimated average position of the five calibration points to calculate
        # perspective transform matrix

        # Get time from middle of video
        time = (get_video_start_time(timeline, video) + get_video_end_time(timeline, video)) / 2

        tmp = []
        # Use only the corner calibration points
        for i in range(1, 5):
            m = linefits[cfg.CALIBRATION_POINT_NAMES[i]]['x'][0]
            b = linefits[cfg.CALIBRATION_POINT_NAMES[i]]['x'][1]
            x_pos = m * time + b

            m = linefits[cfg.CALIBRATION_POINT_NAMES[i]]['y'][0]
            b = linefits[cfg.CALIBRATION_POINT_NAMES[i]]['y'][1]
            y_pos = m * time + b

            tmp.append([cfg.CALIBRATION_POINT_LOCATIONS[i][0] + x_pos, cfg.CALIBRATION_POINT_LOCATIONS[i][1] + y_pos])

        # Note: in OpenCV, y is positive downwards
        # In Pupil Labs software, y is positive upwards
        # The y-axis is flipped when applying the transform in 'gaze_to_frame.py'
        pts1 = np.float32(tmp)
        pts2 = np.float32([cfg.CALIBRATION_POINT_LOCATIONS[1],
                           cfg.CALIBRATION_POINT_LOCATIONS[2],
                           cfg.CALIBRATION_POINT_LOCATIONS[3],
                           cfg.CALIBRATION_POINT_LOCATIONS[4]])

        mat = cv2.getPerspectiveTransform(pts1, pts2)

        def correct_coordinates(x, y):
            tmp = np.float32([[[x, y]]])
            corr_tmp = cv2.perspectiveTransform(tmp, mat)
            return corr_tmp[0, 0]

        return correct_coordinates

    return get_transform_matrix_at_time


if __name__ == "__main__":
    pass
