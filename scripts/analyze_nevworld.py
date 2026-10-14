from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "raw"
PROCESSED_DIR = ROOT / "data" / "processed"


def load_events(raw_dir: Path) -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []
    for path in sorted(raw_dir.glob("*.jsonl")):
        with path.open("r", encoding="utf-8") as handle:
            for line in handle:
                if not line.strip():
                    continue
                events.append(json.loads(line))
    return events


def summarize_events(events: list[dict[str, Any]]) -> dict[str, Any]:
    event_counts = Counter(event["type"] for event in events)
    snapshots = [event for event in events if event["type"] == "world_snapshot"]

    activity_counts = Counter(
        event["activity"]
        for event in events
        if event["type"] == "villager_activity_changed"
    )
    need_counts = Counter(
        event["need_type"]
        for event in events
        if event["type"] == "villager_need_changed"
    )
    social_interaction_counts = Counter(
        event["interaction_type"]
        for event in events
        if event["type"] == "social_interaction"
    )
    prey_counts = Counter(
        event["prey_type"]
        for event in events
        if event["type"] == "hunt_completed"
    )
    resource_changes: dict[str, int] = defaultdict(int)
    for event in events:
        if event["type"] == "resource_changed":
            resource_changes[event["resource_type"]] += int(event["amount_delta"])

    if snapshots:
        pop_series = [int(event["population"]) for event in snapshots]
        wood_series = [int(event["wood_stock"]) for event in snapshots]
        food_series = [int(event["food_stock"]) for event in snapshots]
        gold_series = [int(event["gold_stock"]) for event in snapshots]
        constructed_series = [int(event["constructed_buildings"]) for event in snapshots]
        tick_series = [int(event["tick"]) for event in snapshots]
        start_snapshot = snapshots[0]
        end_snapshot = snapshots[-1]
    else:
        pop_series = []
        wood_series = []
        food_series = []
        gold_series = []
        constructed_series = []
        tick_series = []
        start_snapshot = {}
        end_snapshot = {}

    per_tick = Counter(event["tick"] for event in events)

    return {
        "schema_version": _first_event(events, "schema_version"),
        "run_id": _first_event(events, "run_id"),
        "seed": _first_event(events, "seed"),
        "total_events": len(events),
        "first_tick": min((int(event["tick"]) for event in events), default=0),
        "last_tick": max((int(event["tick"]) for event in events), default=0),
        "event_counts": dict(sorted(event_counts.items())),
        "activity_counts": dict(sorted(activity_counts.items())),
        "need_counts": dict(sorted(need_counts.items())),
        "social_interaction_counts": dict(sorted(social_interaction_counts.items())),
        "prey_counts": dict(sorted(prey_counts.items())),
        "resource_changes": dict(sorted(resource_changes.items())),
        "population_peak": max(pop_series, default=0),
        "population_end": int(end_snapshot.get("population", 0)),
        "population_start": int(start_snapshot.get("population", 0)),
        "constructed_buildings_peak": max(constructed_series, default=0),
        "constructed_buildings_end": int(end_snapshot.get("constructed_buildings", 0)),
        "wood_stock_start": int(start_snapshot.get("wood_stock", 0)),
        "wood_stock_end": int(end_snapshot.get("wood_stock", 0)),
        "food_stock_start": int(start_snapshot.get("food_stock", 0)),
        "food_stock_end": int(end_snapshot.get("food_stock", 0)),
        "gold_stock_start": int(start_snapshot.get("gold_stock", 0)),
        "gold_stock_end": int(end_snapshot.get("gold_stock", 0)),
        "tick_count": len(per_tick),
        "tick_activity": {str(tick): int(count) for tick, count in sorted(per_tick.items())},
        "snapshots_total": len(snapshots),
        "tick_range": [min(tick_series, default=0), max(tick_series, default=0)],
    }


def _first_event(events: list[dict[str, Any]], key: str) -> Any:
    for event in events:
        if key in event:
            return event[key]
    return None


def write_csv(rows: list[dict[str, Any]], path: Path) -> None:
    if not rows:
        return
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def write_outputs(summary: dict[str, Any], raw_dir: Path, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)

    event_rows = [
        {"event_type": name, "count": count}
        for name, count in summary["event_counts"].items()
    ]
    write_csv(event_rows, output_dir / "event_counts.csv")

    tick_rows = [
        {"tick": tick, "event_count": count}
        for tick, count in summary["tick_activity"].items()
    ]
    write_csv(tick_rows, output_dir / "events_by_tick.csv")

    with (output_dir / "summary.json").open("w", encoding="utf-8") as handle:
        json.dump(summary, handle, indent=2, sort_keys=True)
        handle.write("\n")

    with (output_dir / "snapshot_preview.json").open("w", encoding="utf-8") as handle:
        snapshots = [
            event
            for event in load_events(raw_dir)
            if event["type"] == "world_snapshot"
        ]
        json.dump(snapshots[:5], handle, indent=2, sort_keys=True)
        handle.write("\n")


def main() -> None:
    events = load_events(RAW_DIR)
    if not events:
        raise FileNotFoundError(f"No JSONL events were found in {RAW_DIR}")

    summary = summarize_events(events)
    write_outputs(summary, RAW_DIR, PROCESSED_DIR)

    print(json.dumps({
        "run_id": summary["run_id"],
        "seed": summary["seed"],
        "total_events": summary["total_events"],
        "first_tick": summary["first_tick"],
        "last_tick": summary["last_tick"],
        "population_peak": summary["population_peak"],
        "event_counts": summary["event_counts"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
