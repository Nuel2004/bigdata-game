# BigData game analysis

This project loads the raw event stream from `data/raw` and summarizes the simulation into processed CSV/JSON outputs under `data/processed`.

## Quick start

```bash
python -m pip install -r requirements.txt
python scripts/analyze_nevworld.py
```

The script reads every `.jsonl` file in `data/raw`, calculates per-event and per-tick summaries, and writes:

- `data/processed/event_counts.csv`
- `data/processed/events_by_tick.csv`
- `data/processed/summary.json`
- `data/processed/snapshot_preview.json`

## Example output

The current dataset captures a simulation with 19,640 events and a peak population of 4 villagers.
