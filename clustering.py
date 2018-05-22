import numpy as np
import os
import matplotlib.pyplot as plt
from scipy.cluster.vq import kmeans, whiten, vq
from heatmap_gen import get_gaze_points


if __name__ == "__main__":
    result_dir = r"C:\Local\sainio\Documents\eyetracking_extraction\result"
    for gaze_points in get_gaze_points(os.path.join(result_dir, "HoneyBee_3840x2160_60_crf12.mp4")):
        temp = np.array(gaze_points, dtype=np.float32)
        #print(temp)
        if len(gaze_points) < 10:
            break
        whitened = whiten(gaze_points)
        codebook, distortion = kmeans(temp, 5)
        print(distortion, end="\t")
        # Plot whitened data and cluster centers in red
        p, d = vq(temp, codebook)
        colors = ["b", "y", "m", "r", "c"]
        for i in range(5):
            k = np.array([z + (w, ) for z, t, w in zip(gaze_points, p, d) if t == i])
            print(k)
            plt.scatter(k[:, 0], k[:, 1], c=colors[i])

        plt.scatter(codebook[:, 0], codebook[:, 1], c='k')
        plt.show()
        #input()
        print()
