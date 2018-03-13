from time import sleep
import cv2
import numpy as np
import os
from csv import reader

def get_calibration_point_intervals(location, recording="000", staring_frame=10):
    """
    Returns calibration point intervals as a list for the given calibration
    video.
    """

    video_file_path = os.path.join(location, recording, "world.mp4")
    video = cv2.VideoCapture(video_file_path)

    csv_file_path = os.path.join(location, recording, "exports")
    assert (len(os.listdir(csv_file_path)) == 1)  # Make sure there is exactly one export result

    csv_file_path = os.path.join(csv_file_path, os.listdir(csv_file_path)[0], "surfaces")
    for item in os.listdir(csv_file_path):
        if item[0:4] == "srf_":
            csv_file_path = os.path.join(csv_file_path, item)

    csvfile = open(csv_file_path)
    datareader = reader(csvfile)

    datareader.__next__()

    trans_mat = np.zeros((3, 3), np.float64)

    corner_coordinates = np.array([(0, 1), (1, 1), (1, 0,), (0, 0)], dtype=np.float64)

    width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # Expected calibration point locations
    # Note, in the eye capture software, y-axis is positive upwards
    # In openCV, it's positive downwards
    cp_radius = 100
    cp_centers = [
        [0.5 * width, 0.5 * height],
        [0.25 * width, 0.75 * height],
        [0.25 * width, 0.25 * height],
        [0.75 * width, 0.25 * height],
        [0.75 * width, 0.75 * height],
    ]
    # Detection thresholds
    cp_start_threshold = 150 # When a calibration point is visible, the sub image average is under this value
    cp_end_threshold = 160  # When point is fading out, it is considered done when the average is over this

    current_point = 0
    cp_start_frame = 0
    cp_end_frame = 0
    started = False
    interval_get = False
    frame = 0

    intervals = []

    while video.grab():
        data = datareader.__next__()
        matrix_string = data[2].split('\n')
        matrix_string_array = [z for z in map(lambda x: x.strip("[").strip("]").strip().strip("["), matrix_string)]
        trans_mat[0] = [z for z in map(lambda x: float(x), matrix_string_array[0].strip().split())]
        trans_mat[1] = [z for z in map(lambda x: float(x), matrix_string_array[1].strip().split())]
        trans_mat[2] = [z for z in map(lambda x: float(x), matrix_string_array[2].strip().split())]

        corners = np.float64(cv2.perspectiveTransform(np.array([corner_coordinates]), trans_mat)[0])

        p = np.zeros(shape=corners.shape, dtype=np.int32)
        i = 0
        for corner in corners:
            p[i] = (corner[0] * width, height - corner[1] * height)
            i += 1
        pts = p.reshape((-1, 1, 2))

        image = video.retrieve()[1]

        trans_mat2 = cv2.getPerspectiveTransform(np.float32(pts),
                                                 np.float32([[0, 0], [width, 0], [width, height], [0, height]]))

        warp = cv2.warpPerspective(image, trans_mat2, dsize=(width, height))

        average = np.average(warp[int(cp_centers[current_point][1]-cp_radius):int(cp_centers[current_point][1]+cp_radius), \
                         int(cp_centers[current_point][0]-cp_radius):int(cp_centers[current_point][0]+cp_radius)])
        print("CP: " + str(current_point) + " Avg: " + str(average))

        cv2.imshow("Full", warp[:, :])
        cv2.imshow("Test", warp[int(cp_centers[current_point][1]-cp_radius):int(cp_centers[current_point][1]+cp_radius), \
                           int(cp_centers[current_point][0]-cp_radius):int(cp_centers[current_point][0]+cp_radius)])
        if frame > staring_frame:
            if average < cp_start_threshold and not started:
                cp_start_frame = frame
                started = True
            if average > cp_end_threshold and started:
                cp_end_frame = frame
                current_point += 1
                started = False
        cv2.waitKey()

        if interval_get:
            intervals.append([cp_start_frame, cp_end_frame])
            cp_start_frame = 0
            cp_end_frame = 0
            interval_get = False

        frame += 1

def get_starting_frame(location, recording="000", threshold=15.):
    """
    Returns zero based index of the frame that is the first frame that is not 
    completely black on the surface.
    location is the base directory of the recording, not including the '000'
    recording is the number of the recording
    threshold is the value for the average of the pixel to determine whether the picture is black or not
    """
    video_file_path = os.path.join(location, recording, "world.mp4")
    video = cv2.VideoCapture(video_file_path)

    csv_file_path = os.path.join(location, recording, "exports")
    assert(len(os.listdir(csv_file_path)) == 1)  # Make sure there is exactly one export result

    csv_file_path = os.path.join(csv_file_path, os.listdir(csv_file_path)[0], "surfaces")
    for item in os.listdir(csv_file_path):
        if item[0:4] == "srf_":
            csv_file_path = os.path.join(csv_file_path, item)

    csvfile = open(csv_file_path)
    datareader = reader(csvfile)

    datareader.__next__()

    trans_mat = np.zeros((3,3), np.float64)

    corner_coordinates = np.array([(0, 1), (1, 1), (1, 0,), (0, 0)], dtype=np.float64)

    width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))

    while video.grab():
        data = datareader.__next__()
        matrix_string = data[2].split('\n')
        matrix_string_array = [z for z in map(lambda x: x.strip("[").strip("]").strip().strip("["), matrix_string)]
        trans_mat[0] = [z for z in map(lambda x: float(x), matrix_string_array[0].strip().split())]
        trans_mat[1] = [z for z in map(lambda x: float(x), matrix_string_array[1].strip().split())]
        trans_mat[2] = [z for z in map(lambda x: float(x), matrix_string_array[2].strip().split())]

        corners = np.float64(cv2.perspectiveTransform(np.array([corner_coordinates]), trans_mat)[0])

        p = np.zeros(shape=corners.shape, dtype=np.int32)
        i = 0
        for corner in corners:
            p[i] = (corner[0] * width, height - corner[1] * height)
            i += 1
        pts = p.reshape((-1,1,2))

        image = video.retrieve()[1]

        trans_mat2 = cv2.getPerspectiveTransform(np.float32(pts),
                                                 np.float32([[0, 0], [width, 0], [width, height], [0, height]]))

        warp = cv2.warpPerspective(image, trans_mat2, dsize=(width, height))

        if np.average(warp, axis=(0,1,2)) > threshold:
            return int(data[0])

if __name__ == "__main__":
    print(get_calibration_point_intervals(r"C:\Local\siivonek\Data\eye_tracking_data\own_test_data\eyetrack_results\6-m-23\calibrations", "001"))
