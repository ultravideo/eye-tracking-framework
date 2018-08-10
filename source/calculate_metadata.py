import numpy as np
import os
import json

def calculate_metadata(root, destination, average_results):
    """
    Calculates line fits for calibration point averages.
    Also calculates some useful statistical properties of given data.
    
    root is the root folder which contains experiment results     
    destination is the folder name where the exported .json is put
    """
    export_root = os.path.abspath(os.path.join(root, "..", "exports"))
    cp_names = ["center",
                "bottom_left",
                "top_left",
                "top_right",
                "bottom_right"]

    dir = os.path.join(export_root, destination)
    if not os.path.isdir(dir):
        os.makedirs(dir)
    filepath = os.path.join(export_root, destination, "statistics.json")

    if os.path.isfile(filepath):
        print("Statistics already exist. Skip processing.")
    else:

        # Calculate line fits and statistical data for average values for each subject
        metadata = {}
        for subject, values in average_results.items():
            #                                               0       1           2           3           4
            # Group error data by calibration point index (center, bottom left, top left, top right, bottom right)
            cp_x = []
            cp_y = []
            # Initialize empty lists for re-arranging average values
            # Ex. the center calibration point errors are all stored in the same list index
            for i in range(5):
                cp_x.append([])
                cp_y.append([])

            for calibration, errors in values.items():
                for i in range(5):
                    # Use pixel values from indexes 2 & 3
                    cp_x[i].append(errors['gaze_error'][cp_names[i]][2])
                    cp_y[i].append(errors['gaze_error'][cp_names[i]][3])

            tmp = {}
            for i in range(5):
                x = range(len(cp_x[i]))
                mx, bx = np.polyfit(x, cp_x[i], 1)
                my, by = np.polyfit(x, cp_y[i], 1)
                x_linefit = {'m': mx,
                             'b': bx}
                y_linefit = {'m': my,
                             'b': by}
                tmp[cp_names[i]] = {"x_error": cp_x[i],
                                    "y_error": cp_y[i],
                                    "x_stdev": np.std(cp_x[i]),
                                    "y_stdev": np.std(cp_y[i]),
                                    "x_variance": np.var(cp_x[i]),
                                    "y_variance": np.var(cp_y[i]),
                                    "x_linefit": x_linefit,
                                    "y_linefit": y_linefit}

            metadata[subject] = tmp

        # Dump data
        with open(filepath, 'w') as file:
            json.dump(metadata, file)
            file.close()

if __name__ == "__main__":
    pass
