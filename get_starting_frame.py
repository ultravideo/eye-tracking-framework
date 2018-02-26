from time import sleep
import cv2
import numpy as np
import os
from csv import reader


def get_starting_frame(location, threshold=15.):
    """
    Returns zero based index of the frame that is the first frame that is not 
    completely black on the surface.
    location is the base directory of the recording, not including the '000'
    threshold is the value for the average of the pixel to determine wether the picture is black or not
    """
    video_file_path = os.path.join(location, "000", "world.mp4")
    video = cv2.VideoCapture(video_file_path)

    csv_file_path = os.path.join(location, "000", "exports")
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
        k = data[2].split('\n')
        k = [z for z in map(lambda x: x.strip("[").strip("]").strip().strip("["), k)]
        trans_mat[0] = [z for z in map(lambda x: float(x), k[0].strip().split())]
        trans_mat[1] = [z for z in map(lambda x: float(x), k[1].strip().split())]
        trans_mat[2] = [z for z in map(lambda x: float(x), k[2].strip().split())]

        k = np.float64(cv2.perspectiveTransform(np.array([corner_coordinates]), trans_mat)[0])

        p = np.zeros(shape=k.shape, dtype=np.int32)
        i = 0
        for item in k:
            p[i] = (item[0] * width, height - item[1] * height)
            i += 1
        pts = p.reshape((-1,1,2))

        image = video.retrieve()[1]

        trans_mat2 = cv2.getPerspectiveTransform(np.float32(pts),
                                                 np.float32([[0, 0], [width, 0], [width, height], [0, height]]))

        warp = cv2.warpPerspective(image, trans_mat2, dsize=(width, height))
        if np.average(warp, axis=(0,1,2)) > threshold:
            return int(data[0])

if __name__ == "__main__":
    print(get_starting_frame(r"C:\Local\sainio\Data\somedata\1-m-54\BasketballDrill_832x480_50_500.y4m"))
