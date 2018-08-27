from sklearn.neighbors import LocalOutlierFactor


def detect_outliers(points, k=10):
    """
    Detect outliers in given time series.
    Use LocalOutlierFactor to for detection.
    Returns an array of indexes of outlying points.
    """
    outlier_indices = []

    clf = LocalOutlierFactor(n_neighbors=k)
    pred = clf.fit_predict(points)

    for idx, i in enumerate(pred):
        if i == -1:
            outlier_indices.append(idx)

    return outlier_indices
