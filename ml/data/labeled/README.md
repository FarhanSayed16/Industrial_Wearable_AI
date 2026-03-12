# Labeled Data Format

For training the activity classifier, raw IMU data must be labeled by segment.

## Label File Format

Create a CSV with columns:

| Column   | Type   | Description                          |
|----------|--------|--------------------------------------|
| start_ts | int    | Start timestamp (Unix ms)            |
| end_ts   | int    | End timestamp (Unix ms)              |
| label    | string | One of: sewing, idle, adjusting, error, break |

**Example `labels.csv`:**

```csv
start_ts,end_ts,label
1704067200000,1704067205000,sewing
1704067205000,1704067210000,idle
1704067210000,1704067215000,adjusting
```

## Labeling Process

1. **Record raw data** — Use `ml/scripts/collect_raw.py` to capture IMU samples during real or simulated work.
2. **Record video (optional)** — Sync video timestamps with raw data for accurate labeling.
3. **Assign labels per segment** — For each time range, assign one of:
   - **sewing** — Active sewing motion
   - **idle** — No motion, waiting
   - **adjusting** — Adjusting fabric, thread, machine
   - **error** — Error state, troubleshooting
   - **break** — Rest break
4. **Save as CSV** — Place in `ml/data/labeled/` with matching timestamp range to raw file.

## Timestamp Sync

- Raw CSV uses `timestamp` in Unix milliseconds.
- Label segments must use the same time base (same recording session).
- Ensure `start_ts` and `end_ts` fall within the raw data's timestamp range.
