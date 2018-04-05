from math import fabs


def detect_outliers(points, k=3, threshold=0.02):
    """
    Detect outliers in given time series.
    Compare each point against every other in the series.
    If point has enough (k) close neighbors, it is valid.
    Returns an array of indexes of outlying points.
    """
    outlier_indices = []
    index = 0
    neighbors = 0
    valid = False
    for value in points:
        compare_index = 0
        # Compare against all other points
        for compare in points:
            # Skip if comparing same index
            if not index == compare_index:
                if fabs(value - compare) < threshold:
                    # Neighbor found
                    neighbors += 1
                    if neighbors >= k:
                        # Enough neighbors found
                        valid = True
                        break
            compare_index += 1
        if not valid:
            # Mark outlier index
            outlier_indices.append(index)
        else:
            valid = False
        neighbors = 0
        index += 1

    return outlier_indices

if __name__ == "__main__":
    test_data = [0.16743906776599998, 0.14541844868066667, 0.1361723209343334, 0.13351754391633325, 0.12619423812424996, 0.128273731672, 0.12537835140980008, 0.09723641158366664, 0.09461620422283334, 0.09347259614660003, 0.09047860394837498, 0.08731934291250015, 0.0825500311843334, 0.08110943549116673, 0.08223218076637501, 0.0832732403411428, 0.08271681089287497, 0.08363548078, 0.08240471480575001, 0.08088253127737499, 0.08075852152225005, 4.64824534545, 0.9355242060237501, 0.6165451567681876, 0.280317778647, 0.18074318328925004, 0.14373327841724992, 0.10335824124524995, 0.052463685622166634, 0.067455980567875, 0.07339693771220007, 0.07655161008125, 0.078306958062625, 0.07953471479837498, 0.07955009629499993, 0.06950624366433333, 0.071458840508, 0.07085134912137503, 0.06856424106074988, 0.06382043436837503, 0.06204559450587499, 0.05955450494710013, 0.054793132457000016]
    print(detect_outliers(test_data))