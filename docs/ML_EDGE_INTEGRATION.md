# ML / Edge Integration

## Dataset Paths (Reproducibility)

| Path | Purpose |
|------|---------|
| `ml/data/raw/` | Raw IMU CSV files (timestamp, ax, ay, az, gx, gy, gz, temp) |
| `ml/data/labeled/` | Labels CSV (start_ts, end_ts, label) — see `ml/data/labeled/README.md` |
| `ml/models/` | Exported joblib model (`activity_model.joblib`) |

**Training:** `python ml/scripts/train.py --synthetic` (no labels) or with `--raw` and `--labels` for real data.

---

## Model Path

Set `MODEL_PATH` in `edge/.env` to the trained model:

```
MODEL_PATH=ml/models/activity_model.joblib
```

Or use absolute path: `MODEL_PATH=D:/Industrial_Wearable_AI/ml/models/activity_model.joblib`

## Workflow

1. **Train model:** `python ml/scripts/train.py --synthetic` (or with real labels)
2. **Export:** Model saved to `ml/models/activity_model.joblib`
3. **Run edge:** `python -m edge.src.main` — edge loads model automatically
4. **Verify:** Edge logs "Model loaded from ..." when model is found

## Feature Parity

- Edge `process_window()` and ML `extract_features_from_window()` use the same:
  - Low-pass filter (α=0.3)
  - 30 features: per-axis mean, std, min, max, zero_crossing_rate
- Window: 3s @ 25 Hz = 75 samples
- Overlap: 50%
