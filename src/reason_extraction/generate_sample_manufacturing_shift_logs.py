from __future__ import annotations

import csv
import random
from datetime import date, timedelta
from pathlib import Path


OUTPUT_PATH = Path("data/input/sample_manufacturing_shift_logs.csv")
RANDOM_SEED = 42
TOTAL_ROWS = 1000

LINES = ["Line1", "Line2", "Line3", "Line4"]
SHIFTS = ["A", "B", "C"]

DOWNTIME_REASONS = [
    "Equipment Failure",
    "Material Shortage",
    "Changeover",
    "Cleaning",
    "Quality Issue",
    "No Downtime",
]

INVALID_TYPES = [
    "missing_line",
    "invalid_shift",
    "defect_exceeds_actual",
    "invalid_downtime",
    "negative_planned_output",
]


def weighted_downtime_reason(record_date: date) -> str:
    """Create a simple before/after improvement story across Jan-Mar 2026."""
    month = record_date.month

    if month == 1:
        weights = {
            "Equipment Failure": 0.40,
            "Material Shortage": 0.18,
            "Changeover": 0.17,
            "Cleaning": 0.12,
            "Quality Issue": 0.10,
            "No Downtime": 0.03,
        }
    elif month == 2:
        weights = {
            "Equipment Failure": 0.25,
            "Material Shortage": 0.18,
            "Changeover": 0.22,
            "Cleaning": 0.13,
            "Quality Issue": 0.10,
            "No Downtime": 0.12,
        }
    else:
        weights = {
            "Equipment Failure": 0.10,
            "Material Shortage": 0.15,
            "Changeover": 0.25,
            "Cleaning": 0.12,
            "Quality Issue": 0.08,
            "No Downtime": 0.30,
        }

    return random.choices(
        population=list(weights.keys()),
        weights=list(weights.values()),
        k=1,
    )[0]


def generate_valid_record(row_num: int) -> dict:
    start_date = date(2026, 1, 1)
    record_date = start_date + timedelta(days=random.randint(0, 89))

    shift = random.choice(SHIFTS)
    line = random.choice(LINES)

    planned_output = random.randint(800, 1200)
    actual_output = int(planned_output * random.uniform(0.85, 1.05))
    actual_output = max(actual_output, 0)

    defect_qty = int(actual_output * random.uniform(0.0, 0.03))

    downtime_reason = weighted_downtime_reason(record_date)

    if downtime_reason == "No Downtime":
        downtime_min = 0
    elif downtime_reason == "Equipment Failure":
        downtime_min = random.randint(25, 120)
    elif downtime_reason == "Material Shortage":
        downtime_min = random.randint(15, 90)
    elif downtime_reason == "Changeover":
        downtime_min = random.randint(20, 100)
    elif downtime_reason == "Cleaning":
        downtime_min = random.randint(10, 60)
    else:
        downtime_min = random.randint(10, 75)

    return {
        "shift_log_id": f"SL{row_num:04d}",
        "date": record_date.isoformat(),
        "shift": shift,
        "line": line,
        "planned_output": planned_output,
        "actual_output": actual_output,
        "defect_qty": defect_qty,
        "downtime_min": downtime_min,
        "downtime_reason": downtime_reason,
        "operator": f"Operator {random.choice(['A', 'B', 'C', 'D', 'E'])}",
        "source_system": random.choice(["Google Form", "Manual CSV Upload", "Legacy Excel Log"]),
    }


def inject_invalid_value(record: dict) -> dict:
    invalid_type = random.choice(INVALID_TYPES)
    record = record.copy()

    if invalid_type == "missing_line":
        record["line"] = ""
    elif invalid_type == "invalid_shift":
        record["shift"] = "D"
    elif invalid_type == "defect_exceeds_actual":
        record["defect_qty"] = int(record["actual_output"]) + random.randint(1, 100)
    elif invalid_type == "invalid_downtime":
        record["downtime_min"] = random.randint(481, 900)
    elif invalid_type == "negative_planned_output":
        record["planned_output"] = -random.randint(1, 300)

    return record


def main() -> None:
    random.seed(RANDOM_SEED)
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    records = []

    normal_count = 940
    invalid_count = 40
    duplicate_count = 20

    for i in range(1, normal_count + invalid_count + 1):
        record = generate_valid_record(i)

        if i > normal_count:
            record = inject_invalid_value(record)

        records.append(record)

    duplicate_candidates = random.sample(records[:normal_count], duplicate_count)

    for i, source_record in enumerate(duplicate_candidates, start=normal_count + invalid_count + 1):
        duplicate_record = source_record.copy()
        duplicate_record["shift_log_id"] = f"SL{i:04d}"
        duplicate_record["operator"] = f"Operator {random.choice(['A', 'B', 'C', 'D', 'E'])}"
        duplicate_record["source_system"] = "Duplicate CSV Upload"
        records.append(duplicate_record)

    random.shuffle(records)

    fieldnames = [
        "shift_log_id",
        "date",
        "shift",
        "line",
        "planned_output",
        "actual_output",
        "defect_qty",
        "downtime_min",
        "downtime_reason",
        "operator",
        "source_system",
    ]

    with OUTPUT_PATH.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)

    print(f"Generated {len(records)} rows: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()