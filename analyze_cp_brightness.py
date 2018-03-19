import cv2
import numpy as np
import os
from csv import reader

def analyze_cp_brightness(location, recording="000"):
    """
    Analyze the brightness level of the regions where calibration points appear
    """
    print("Arse")
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
    cp_radius = 120
    cp_centers = [
        [0.5 * width, 0.5 * height],
        [0.27 * width, 0.70 * height],
        [0.27 * width, 0.30 * height],
        [0.73 * width, 0.30 * height],
        [0.73 * width, 0.70 * height],
    ]

    min_brightness = [255, 255, 255, 255, 255]
    frame = 0

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

        # Find the minimum brightness for all the expected calibration point locations
        for i in range(5):
            average = np.average(
                warp[int(cp_centers[i][1] - cp_radius):int(cp_centers[i][1] + cp_radius), \
                int(cp_centers[i][0] - cp_radius):int(cp_centers[i][0] + cp_radius)])
            if average < min_brightness[i]:
                min_brightness[i] = average

    return min_brightness

if __name__ == 'main':
    print("Eat my ass")
    print(analyze_cp_brightness(
        r"C:\Local\siivonek\Data\eye_tracking_data\own_test_data\eyetrack_results\22-f-25\calibrations", "009"))