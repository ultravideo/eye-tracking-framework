def compress_gaze_points(data):
    """
    Calculate the averages of gaze points on the same frame and
    return compressed gaze data.
    """
    print("Compressing data points found in same frames")
    print("Original data size: " + str(len(data)))

    tmp_data = []
    frame = int(data[0][0])
    sum_x = 0
    sum_y = 0
    points_in_frame = 0

    for row in data:
        if frame == int(row[0]):
            sum_x += float(row[2])
            sum_y += float(row[3])
            points_in_frame += 1
        else:
            avg_x = sum_x / points_in_frame
            avg_y = sum_y / points_in_frame
            tmp_data.append([frame, avg_x, avg_y])
            points_in_frame = 1
            frame = int(row[0])
            sum_x = float(row[2])
            sum_y = float(row[3])

    print("Compressed data size: " + str(len(tmp_data)))

    return tmp_data