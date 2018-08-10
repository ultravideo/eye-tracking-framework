import sys
import os
from multiprocessing import Pool
from shutil import copy
from gaze_to_frame import gaze_to_frame
from get_correction_func import get_correction_func

ignore_person = ['0-f-35',
                 '16-f-43',
                 '28-f-23',
                 '32-f-26',
                 '33-f-36']

def make_dir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)


def parse_log(log):
    videos = []
    with open(log) as log_file:
        for row in log_file:
            row = row.split()
            if row[2] == "video":
                videos.append(row[3])
    return videos


def parse_person(subject):
    if subject in ignore_person:
        print("Skipping", subject)
        return
    result_dir = r"D:\actual_eyetrack_results"

    if len(sys.argv) >= 2:
        output_dir = sys.argv[1]
    else:
        output_dir = "."

    subject_path = os.path.join(result_dir, subject)
    if not os.path.isdir(subject_path):
        return

    make_dir(os.path.join(output_dir, subject))



    videos = parse_log(os.path.join(subject_path, "log.txt"))
    count = 1

    for video in videos:
        # Instead of the lambda this should be a call to a function that calculates the parameters for the correction
        # function and returns a function that uses those parameters to calculate the corrected coordinates
        correction_func = get_correction_func(subject_path, video)

        make_dir(os.path.join(output_dir, video))
        frame_rate = int(video.split("_")[2][0:2])
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
    result_dir = r"D:\actual_eyetrack_results"

    # parse_person('17-m-21')

    with Pool(processes=16) as pool:
        pool.map(parse_person, os.listdir(result_dir))


if __name__ == "__main__":
    main()
