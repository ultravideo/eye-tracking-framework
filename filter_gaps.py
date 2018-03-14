from csv import reader
import numpy as np

# Index definitions
WORLD_TIMESTAMP = 0
WORLD_FRAME_IDX = 1
GAZE_TIMESTAMP = 2
X_NORM = 3
Y_NORM = 4
X_SCALED = 5
Y_SCALED = 6
ON_SRF = 7
CONFIDENCE = 8

GAZE_STAMP_THRESHOLD = 0.0043  # If time between two gaze data points is larger than this, there's a gap
BLINK_REMOVE_THRESHOLD = 0.2  # This amount in seconds is removed before and after a detected gap
CLUSTER_THRESHOLD = 5  # If there are less than 5 gaps in a cluster, ignore gap


def filter_gaps(csv_file_path, start_frame):
    data = []
    indexes = [WORLD_FRAME_IDX, GAZE_TIMESTAMP, X_NORM, Y_NORM]  # Select the indexes to be saved
    gaps = []  # Find gaps in data points
    previous_time = 0.0

    with open(csv_file_path) as csvfile:
        datareader = reader(csvfile)
        # Skip header
        datareader.__next__()

        for row in datareader:
            # world_timestamp, world_frame_idx, gaze_timestamp, x_norm, y_norm, x_scaled, y_scaled, on_srf, confidence
            if int(row[WORLD_FRAME_IDX]) >= start_frame:
                data.append([row[i] for i in indexes])

                if (float(row[GAZE_TIMESTAMP]) - previous_time) > GAZE_STAMP_THRESHOLD:
                    # Gap detected, add timestamp to list
                    gaps.append(float(row[GAZE_TIMESTAMP]))
                previous_time = float(row[GAZE_TIMESTAMP])
            else:
                previous_time = float(row[GAZE_TIMESTAMP])

    print("Gaps found " + str(len(gaps)))

    # Analyze gaps. Leave only significant gaps or gap clusters
    final_gaps = []
    cluster_start = 0
    cluster_end = 0
    gap_threshold = 0.1
    gaps_in_cluster = 0
    written = False

    for gap in gaps:
        # print(str(gap))
        if cluster_start == 0:
            cluster_start = gap
            cluster_end = gap
            gaps_in_cluster += 1
        else:
            if (gap - cluster_end) < gap_threshold:
                cluster_end = gap
                gaps_in_cluster += 1
                written = False
            else:
                final_gaps.append([gaps_in_cluster, cluster_start, cluster_end])
                written = True
                cluster_start = gap
                cluster_end = gap
                gaps_in_cluster = 1

    if not written:
        final_gaps.append([gaps_in_cluster, cluster_start, cluster_end])

    for gap in final_gaps:
        print("Gaps: " + str(gap[0]) + " Time " + str(gap[1]) + " - " + str(gap[2]))

    # Some variables for drawing a plot later
    # plot_x_start = data[0][GAZE_TIMESTAMP]
    # plot_x_end = data[-1][GAZE_TIMESTAMP]

    # Blink removal. Create new data structure by filtering out entries around found gaps
    filtered_data = []
    eliminated_data = []
    next_gap = 0

    # for row in data:
    #     if float(row[1]) > (gaps[next_gap] + BLINK_REMOVE_THRESHOLD):
    #         # Passed current gap
    #         if not next_gap == len(gaps) - 1:
    #             next_gap += 1
    #
    #     if (float(row[1]) > (gaps[next_gap] - BLINK_REMOVE_THRESHOLD)) and (float(row[1]) < (gaps[next_gap] + BLINK_REMOVE_THRESHOLD)):
    #         # Current items timestamp is inside elimination threshold
    #         eliminated_data.append(row)
    #     else:
    #         filtered_data.append(row)

    for row in data:
        if float(row[1]) > final_gaps[next_gap][2]:
            # Passed current gap
            if not next_gap == len(final_gaps) - 1:
                next_gap += 1

        # Ignore gap if gap time is too short, or the cluster is too small
        if final_gaps[next_gap][2] - final_gaps[next_gap][1] < BLINK_REMOVE_THRESHOLD or final_gaps[next_gap][
            0] < CLUSTER_THRESHOLD:
            if (float(row[1]) > (final_gaps[next_gap][1] - BLINK_REMOVE_THRESHOLD)) and (
                        float(row[1]) < (final_gaps[next_gap][2] + BLINK_REMOVE_THRESHOLD)):
                # Current items timestamp is inside elimination threshold
                eliminated_data.append(row)
            else:
                filtered_data.append(row)
        else:
            filtered_data.append(row)

    print("Filtered data size " + str(len(filtered_data)))
    print("Eliminated data size " + str(len(eliminated_data)))

    # Return resulting filtered data
    return filtered_data
