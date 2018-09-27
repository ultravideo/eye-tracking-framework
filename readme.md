# Eye tracking data error correction

System for correcting error caused by eye tracking glasses during data collection. The system is designed to approximate and correct systematic error caused by the glasses moving on the subjects head during an experiment. For more detailed info, read the corresponding publication (link here if/when the paper is published)

The system was used to correct results gathered by using Pupil Mobile Eye Tracking Headset (https://pupil-labs.com/pupil/).

## Setting up

To run the code, you will need Python 3.6 with OpenCV, numpy and Scikit-Learn installed.

The system will work out of the box if used with results from Pupil Labs Eye Tracking Headset. Using with other eye tracking systems will require modification of the code.

Since the system was designed to process data exported with the Pupil Labs software, the system assumes the following:
1. The folder structure is similar to the one created by Pupil Labs software
2. Contents (data columns) of the exported gaze data files are similar

The system expects the gaze data files to be found under the following path:
```
<RESULTS_ROOT>/<SUBJECT>/<VIDEO>/<TEST_ID>/exports/<FRAMES>/surfaces/
```
The gaze data file contains the following fields in csv-format:
```
world_timestamp, world_frame_idx, gaze_timestamp, x_norm, y_norm, x_scaled, y_scaled, on_srf, confidence
```

## Provided data

The raw eye tracking data collected during our experiment is included inside the data folder. In addition, modified versions of the data files with only the gaze data (uncorrected and corrected) are also included for easy comparison.

The test sequences used in the eye tracking experiment are not provided due to filesize limitations.

## License

This project is licensed under the BSD 2 License - see the [LICENSE.md](LICENSE.md) file for details
