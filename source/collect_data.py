import os
import fnmatch
import shutil

root = r"C:\Local\siivonek\Data\eye_tracking_data\own_test_data\eyetrack_results"
export_path_root = os.path.join(root, "export")

# create test data folder if it doesn't exists
if not os.path.isdir(export_path_root):
    os.makedirs("export")

# Go through all experiment folders
# Each folder contains all data for one experiment instance
for dir in os.listdir(root):

    print("Exporting " + dir)

    if os.path.isdir(os.path.join(root, dir)):
        path_exp = os.path.join(root, dir)
        # debug
        # print(path_exp)

        # subdirs = os.listdir(path_exp)
        subdirs = next(os.walk(path_exp))[1]
        print("  Objects found " + str(len(subdirs)))
        # Go through each individual video folder
        # Each video folder contains all data for said video
        for vid in subdirs:
            if os.path.isdir(os.path.join(path_exp, vid)):
                path_vid = os.path.join(path_exp, vid)
                # debug
                # print("  " + vid)

                # Go through each instance of current video
                for vid_1 in os.listdir(path_vid):
                    if os.path.isdir(os.path.join(path_vid, vid_1)):
                        path_vid_1 = os.path.join(path_vid, vid_1)
                        # debug
                        # print("    " + vid_1)

                        # Inside this folder should be the exports folder
                        # with another folder inside with a frame count
                        # as its name

                        # Check if exports dir exists
                        if "exports" in os.listdir(path_vid_1):
                            # debug
                            path_exports = os.path.join(path_vid_1 + "\exports")

                            # find the folder with frame range, and enter folder "surfaces"
                            path_final = os.path.join(path_exports, os.listdir(path_exports)[0] + "\surfaces")

                            # Find correct file
                            filename = "_"
                            for _, _, files in os.walk(path_final):
                                for name in files:
                                    if fnmatch.fnmatch(name, "gaze_positions*"):
                                        filename = name;

                            copy_file_path = os.path.join(path_final, filename)
                            # Copy all necessary files to a more accessible location
                            # We will also duplicate the file structure so results are arranged by video
                            # and by subject

                            # Copy by subject
                            export_filename = dir + "_" + vid.split('.')[0] + "_" + vid_1 + "_" + filename[:14] + ".csv"
                            export_path = os.path.join(export_path_root, dir)

                            # Create folder if it doesn't exist
                            if not os.path.isdir(export_path):
                                os.makedirs(export_path)
                            shutil.copyfile(copy_file_path, os.path.join(export_path, export_filename))

                            # Copy by video
                            export_path = os.path.join(export_path_root, vid.split('_')[0])
                            if not os.path.isdir(export_path):
                                os.makedirs(export_path)
                            shutil.copyfile(copy_file_path, os.path.join(export_path, export_filename))

                            # debug
                            # print(os.path.join(export_path, export_filename))
                            # print(copy_file_path)
                            # print(os.path.join(export_path, export_filename))
    else:
        print("  Not a directory")
