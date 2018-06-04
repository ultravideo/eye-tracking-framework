import os


def get_video_order(subject):
    """
    Get the showing order of test videos for the given subject.    
    """
    log_file_path = os.path.join(subject, "log.txt")

    order = []
    with open(log_file_path) as logfile:
        for line in logfile:
            if "started video" in line:
                substr = line.split("started video ")
                substr2 = substr[1].split(" ")
                order.append(substr2[0])

    return order


if __name__ == "__main__":
    print(get_video_order("C:\Local\siivonek\Data\eye_tracking_data\own_test_data\eyetrack_results", "23-f-25"))
