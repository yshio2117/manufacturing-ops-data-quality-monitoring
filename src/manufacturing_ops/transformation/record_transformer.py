import uuid
import os
from dateutil import parser
from datetime import timezone, datetime

# fixed namespace for generating UUID v5 to ensure consistency of shift_log_id across different runs and environments.
APP_NAMESPACE = uuid.UUID(os.getenv("UUID_STRING")) 


def generate_uuid_v5(record_date, shift, line):
    """ Generate UUID v5 from record_date, shift, line """

    return str(uuid.uuid5(APP_NAMESPACE, f"{record_date}|{shift}|{line}"))


def add_shift_log_id(records):
    """
    Add shift_log_id using normalized business key fields:
    production_date, shift_normalized, line_normalized.

    shift_log_id is generated only when all key fields are valid.
    """

    for record in records:
        production_date = record.get("production_date")
        shift = record.get("shift_normalized")
        line = record.get("line_normalized")

        key_is_valid = (
            production_date is not None
            and shift in ("A", "B", "C")
            and line is not None
            and bool(str(line).strip())
        )

        if not key_is_valid:
            record["shift_log_id"] = None
            continue

        record["shift_log_id"] = generate_uuid_v5(
            production_date,
            shift,
            line,
        )

    return records


DATE_FORMATS = (
    "%Y-%m-%d",
    "%Y/%m/%d",
    "%Y.%m.%d",
    "%d-%m-%Y",
    "%d/%m/%Y",
    "%d.%m.%Y",
)

def normalize_date(raw_date):
    """ Normalize raw_date to YYYY-MM-DD."""

    if raw_date is None:
        return None

    raw_date = str(raw_date).strip()

    if not raw_date:
        return None

    for fmt in DATE_FORMATS:
        try:
            return (
                datetime.strptime(raw_date, fmt)
                .date()
                .isoformat()
            )
        except ValueError:
            continue

    return None


def parse_int(value):
    try:
        if value is None or not str(value).strip():
            return None
        return int(str(value).strip())
    except ValueError:
        return None


def normalize_records(records):
    """
    Normalize shift_log_id (business key) fields and parse numeric fields while preserving raw source values.

    Adds:
        production_date
        shift_normalized
        line_normalized
        planned_output_int
        actual_output_int
        defect_qty_int
        downtime_min_int

    Notes:
        - Raw values (date, shift, line) are preserved.
        - production_date is normalized to YYYY-MM-DD.
        - If date parsing fails, production_date is set to None.
    """



    for record in records:

        # date to production_date
        record["production_date"] = normalize_date(
            record.get("date")
        )

        # shift to shift_normalized
        raw_shift = record.get("shift")

        if raw_shift is None:
            record["shift_normalized"] = None
        else:
            normalized_shift = str(raw_shift).strip().upper()
            record["shift_normalized"] = (
                normalized_shift if normalized_shift else None
            )

        # line to line_normalized
        raw_line = record.get("line")

        if raw_line is None:
            record["line_normalized"] = None
        else:
            normalized_line = str(raw_line).strip()
            record["line_normalized"] = (
                normalized_line if normalized_line else None
            )

        # Numeric parsing
        record["planned_output_int"] = parse_int(
            record.get("planned_output")
        )

        record["actual_output_int"] = parse_int(
            record.get("actual_output")
        )

        record["defect_qty_int"] = parse_int(
            record.get("defect_qty")
        )

        record["downtime_min_int"] = parse_int(
            record.get("downtime_min")
        )

    return records


def split_records_by_validity(validated_records):
    """ Split records into valid and invalid records based on 'is_valid' key in each record."""
       

    valid_records = []
    invalid_records = []
    for record in validated_records:
        if record['is_valid']:
            valid_records.append(record)
        else:
            invalid_records.append(record)

    return valid_records, invalid_records





def filter_columns(record):
    """ Drop unnecessary columns for kpi table """
    
    keys_to_drop = ("date_iso", "is_duplicate", "invalid_reason", "is_valid")
    
    for key in keys_to_drop:
        record.pop(key, None)

    return record


def build_shift_log_kpi_records(validated_records):
    """ Cauculate KPIs and build shift_log_kpi records """

    kpi_records = []

    for record in validated_records:
        if not record.get("is_valid"):
            continue

        planned_output = record["planned_output"]
        actual_output = record["actual_output"]
        defect_qty = record["defect_qty"]
        downtime_min = record["downtime_min"]

        kpi_record = record.copy()
        # Drop unnecessary columns for kpi table
        kpi_record = filter_columns(kpi_record)

        kpi_record["production_achievement"] = (
            actual_output / planned_output if planned_output else None
        )
        kpi_record["defect_rate"] = (
            defect_qty / actual_output if actual_output else None
        )
        kpi_record["downtime_rate"] = downtime_min / 480

        kpi_records.append(kpi_record)

    return kpi_records
