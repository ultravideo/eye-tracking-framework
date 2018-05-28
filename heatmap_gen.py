from math import sqrt
import numpy as np
import os
import cv2


def euclidean_distance(center, point):
    return sqrt((center[0] - point[0]) ** 2 + (center[1] - point[1]) ** 2)


def generate_gaze_center(image_width):
    gaze_size = image_width // 15
    gaze_size += gaze_size % 2
    arr = np.zeros(shape=(gaze_size, gaze_size), dtype=np.float64)
    center = (gaze_size / 2, gaze_size / 2,)
    for y in range(gaze_size):
        for x in range(gaze_size):
            arr[y, x] = max(0., gaze_size // 2 - euclidean_distance(center, (x, y)))

    return gaze_size, arr


def get_gaze_points(video):
    frames = [[] for i in range(1000)]
    maximum = 0
    for person in os.listdir(video):
        with open(os.path.join(video, person), "r") as gaze_file:
            gaze_file.__next__()
            for row in gaze_file:
                data = [float(x) for x in row.split(",")]
                frames[int(data[0])].append((int(round(data[1])), (int(round(data[2])))))
                maximum = max(maximum, data[0])

    return frames[:int(maximum)]


def write_video(video, gaze_points, out_video_name):
    print("Started: " + os.path.basename(video))
    resolution = [int(x) for x in os.path.basename(video).split("_")[1].split("x")]
    input_video = cv2.VideoCapture(video)
    out_video = cv2.VideoWriter(out_video_name, cv2.VideoWriter_fourcc(*"X264"), input_video.get(cv2.CAP_PROP_FPS),
                                (resolution[0], resolution[1]), 1)
    gaze_size, gaze_center = generate_gaze_center(int(resolution[0]))
    offset = gaze_size // 2
    for i, row in enumerate(gaze_points):
        if i and i % 50 == 0:
            print("{}th frame of {}.".format(i, os.path.basename(video)))
        blank = np.zeros(shape=(resolution[1] + gaze_size, resolution[0] + gaze_size), dtype=np.float64)
        for gaze in row:
            blank[gaze[1]:gaze[1] + gaze_size, gaze[0]:gaze[0] + gaze_size] += gaze_center
        a = np.zeros(blank.shape, np.uint8)
        a = cv2.normalize(blank, a, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX, dtype=np.uint8())
        b = cv2.applyColorMap(a, cv2.COLORMAP_JET)

        suc, image = input_video.read()
        if not suc:
            print("too many frames " + video)
            break
        out_video.write(cv2.addWeighted(b[offset:-offset, offset:-offset], 0.7, image, 0.3, 0))

    out_video.release()
    input_video.release()


if __name__ == "__main__":
    result_dir = r"C:\local\sainio\documents\eyetracking_extraction\result"
    video_dir = r"C:\Local\sainio\Data\eye_tracking_final_sequences_y4m"
    output_dir = r"C:\local\sainio\documents\eyetracking_extraction\result\videos"

    for video in os.listdir(video_dir):
        if video == "blank":
            continue
        temp = get_gaze_points(os.path.join(result_dir, video))
        write_video(os.path.join(video_dir, video), temp, os.path.join(output_dir, video.split(".")[0] + ".mkv"))
