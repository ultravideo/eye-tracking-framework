import os

def get_calibration_folders(root):
    """
    Returns calibration folders for each test subject inside root folder.
    Also returns each calibration video folder inside calibration folder.
    Returned values are stored in dictionary format.
    """

    directories = [dir for dir in os.listdir(root) if os.path.isdir(os.path.join(root, dir))]
    print("Subjects found " + str(len(directories)))

    output = {}

    for subject in directories:

        if os.path.isdir(os.path.join(root, subject)):
            subject_dir = os.path.join(root, subject)
            calib_dir = os.path.join(subject_dir, "calibrations")

            # Debug
            # print(subject)
            # print(calib_dir)

            # Check if directory contains calibrations
            if os.path.isdir(calib_dir):
                calibrations = next(os.walk(calib_dir))[1]                        
                output[subject] = calibrations

    return output

if __name__ == "__main__":
    print(get_calibration_folders("C:\Local\siivonek\Data\eye_tracking_data\own_test_data\eyetrack_results"))