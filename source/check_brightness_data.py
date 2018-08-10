# Check brightness data for anomalies

import json
import os

root = r"C:\Local\siivonek\Data\eye_tracking_data\own_test_data\eyetrack_results"
datafile = os.path.join(root, "cp_brightness.json")

anomalies = []

with open(datafile) as file:
    stuff = json.load(file)
    for subject in stuff:
        print(subject[0])
        for calib in subject[1]:
            print(calib)
            for i in range(5):
                if calib[1][i] < 130:
                    anomalies.append([subject[0], calib])
                    break

print("Anomalies in data: " + str(len(anomalies)))

if len(anomalies) > 0:
    for i in anomalies:
        print(i)
