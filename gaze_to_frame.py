import os
import numpy as np
from math import floor

from csv import reader
from get_starting_frame import get_starting_frame


def average_gaze(data):
    x = 0
    y = 0
    for item in data:
        x += item[0]
        y += item[1]

    return x / len(data), y / len(data),


def in_frame(point, topright):
    if point[0] < 0 or point[1] < 0:
        return False
    if point[0] > topright[0] or point[1] > topright[1]:
        return False
    return True


def gaze_to_frame(location, recording, framerate=60, correction_function=lambda x, y: (x, y)):
    """
    location is the path to the video about the recording not including the number "000"
    recording is the number
    framerate is the framerate of the video that the recording is about
    correction_function should be a function that takes x and y coordinate and returns a tuple containing
    the corrected x and y coordinate
    Returns an array containing the gaze for each frame, might be missing some (<10) frames at the end
    """
    start_frame = get_starting_frame(location, recording)

    gaze_file_path = os.path.join(location, recording, "exports")
    assert (len(os.listdir(gaze_file_path)) == 1)  # Make sure there is exactly one export result

    gaze_file_path = os.path.join(gaze_file_path, os.listdir(gaze_file_path)[0], "surfaces")
    for item in os.listdir(gaze_file_path):
        if item[0:4] == "gaze":
            gaze_file_path = os.path.join(gaze_file_path, item)
            break

    assert (gaze_file_path[-4:] == ".csv")  # Make sure gaze file was actually found

    resolution = [int(x) for x in os.path.basename(location).split("_")[1].split("x")]
    frametime = 1. / framerate

    # For validating the data the threshold in the csv file can't really be used since the capture software
    # has already removed the worst offenders so we use this value to determine if multiple values have been
    # removed in succession meaning that the watcher blinked
    threshold = int(floor(240. / framerate - 0.01))

    final_data = []

    with open(gaze_file_path) as gaze_file:
        gaze_reader = reader(gaze_file)
        gaze_reader.__next__()  # skip the header row
        data = gaze_reader.__next__()

        frame_number = 1

        # Skip the black frames
        while int(data[1]) != start_frame:
            data = gaze_reader.__next__()

        initial_timestamp = float(data[2])  # used for determining to which frame the gaze should be tied
        data_points = []

        for row in gaze_reader:
            if initial_timestamp + frametime < float(row[2]):
                frame_number += 1
                if len(data_points) < threshold:
                    final_data.append(None)
                else:
                    temp = average_gaze(data_points)
                    x, y = correction_function(temp[0], temp[1])
                    x = resolution[0]*x
                    y = resolution[1]*y

                    if in_frame((x, y), resolution):
                        final_data.append((x, y,))
                    else:
                        final_data.append(None)
                data_points = []
                initial_timestamp += frametime

            data_points.append((float(row[3]), float(row[4]),))

    return final_data


if __name__ == "__main__":
    gaze_to_frame(r"C:\Local\sainio\Data\somedata\11-m-25\rushHour_1920x1080_50.y4m", "000", 50)
