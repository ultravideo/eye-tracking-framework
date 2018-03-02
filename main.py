import os
from gaze_to_frame import gaze_to_frame


def parse_log(log):
    videos = []
    with open(log) as log_file:
        for row in log_file:
            row = row.split()
            if row[2] == "video":
                videos.append(row[3])
    return videos


def main():
    result_dir = r"D:\actual_eyetracking_results"

    for subject in os.listdir(result_dir):
        subject = os.path.join(result_dir, subject)
        if not os.path.isdir(subject):
            continue

        # Instead of the lambda this should be a call to a function that calculates the parameters for the correction
        # function and returns a function that uses those parameters to calculate the corrected coordinates
        correction_func = lambda x, y, seq: (x, y)

        videos = parse_log(os.path.join(subject, "log.txt"))
        count = 1

        for video in videos:
            frame_rate = int(video.split("_")[2][0:2])
            data = gaze_to_frame(os.path.join(subject, video), "000", frame_rate,
                                 lambda x, y: correction_func(x, y, count))

            # Write the data to file 


if __name__ == "__main__":
    main()
