# Activity Model Card

## Training
- **Date:** 2026-02-04T13:59:43.551659
- **Raw data:** raw_20260204_135827.csv
- **Labels:** synthetic
- **Samples:** 17 windows

## Parameters
- **Window:** 3s (75 samples @ 25 Hz)
- **Overlap:** 50%
- **Model:** RandomForestClassifier (n_estimators=100, max_depth=10)

## Features (30)
Per axis (ax,ay,az,gx,gy,gz): mean, std, min, max, zero_crossing_rate

## Metrics
- **Accuracy:** 100.00%
