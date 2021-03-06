import sys
import os
from multiprocessing import Pool
from shutil import copy

import config as cfg
from gaze_to_frame import gaze_to_frame
from get_correction_func import get_correction_func_dispenser


def make_dir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)


# Get the video folder names from the log written by the experiment control script
def parse_log(log):
    videos = []
    with open(log) as log_file:
        for row in log_file:
            row = row.split()
            if row[2] == "video":
                videos.append(row[3])
    return videos


def parse_person(subject):
    if subject in cfg.IGNORE_PERSON:
        print("Skipping", subject)
        return

    if len(sys.argv) >= 2:
        output_dir = sys.argv[1]
    else:
        output_dir = cfg.DEFAULT_OUTPUT_DIRECTORY

    subject_path = os.path.join(cfg.RESULTS_DIRECTORY, subject)
    if not os.path.isdir(subject_path):
        return

    make_dir(os.path.join(output_dir, subject))

    videos = parse_log(os.path.join(subject_path, "log.txt"))

    function_dispenser = get_correction_func_dispenser(subject_path)

    for video in videos:
        # Get the correction factor for this video
        correction_func = function_dispenser(video)

        make_dir(os.path.join(output_dir, video))
        frame_rate = int(video.split("_")[2][0:2])

        # The recording is "000" for all normal videos
        # Only the calibrations folder contains recording numbers other that "000"
        data = gaze_to_frame(os.path.join(subject_path, video), "000", frame_rate,
                             correction_func)

        result_file_path = os.path.join(output_dir, video, "{}.csv".format(subject))

        with open(result_file_path, "w") as gaze_data:
            gaze_data.write("frame_index,x_coord,y_coord\n")
            for index, gaze in enumerate(data):
                if gaze:
                    gaze_data.write("{},{},{}\n".format(index, gaze[0], gaze[1]))

        copy(result_file_path, os.path.join(output_dir, subject, "{}.csv".format(video)))


def main():
    if not cfg.config_check():
        return
    with Pool(processes=16) as pool:
        pool.map(parse_person, os.listdir(cfg.RESULTS_DIRECTORY))


if __name__ == "__main__":
    main()
