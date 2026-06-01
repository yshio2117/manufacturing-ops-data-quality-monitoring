from datetime import datetime, date, timezone, timedelta


def validate_record_date(record):
    """
    Validate date and date_iso.

    Validation rules:
    1. if date is empty/None → invalid (MISSING)
    2. if date exists but date_iso is None → invalid (PARSE_FAILED)
    3. if date_iso exists but not in UTC nor parseable → invalid (NOT_UTC or PARSE_FAILED)

    If date cannot be converted into an ISO format, 
    set 'shift_log_id' to None, to prevent the same record from being assigned different ids due to inconsistent date formats.
    """

    reasons = list(record.get("invalid_reason", []))

    raw = record.get("date")
    iso = record.get("date_iso")

    raw_is_missing = (raw is None) or (isinstance(raw, str) and not raw.strip()) or (not isinstance(raw, str))

    # 1) Missing raw date
    if raw_is_missing:
        reasons.append("date is missing")

    # 2) Raw exists but normalization filed
    raw_has_value = isinstance(raw, str) and bool(raw.strip())
    if raw_has_value and iso is None:
        reasons.append("date parse failed")

    # 3) If iso exists, validate it is parseable and UTC
    if iso is not None:
        try:
            dt = datetime.fromisoformat(iso)

            # Must be timezone-aware and in UTC
            if dt.tzinfo is None:
                reasons.append("date is not UTC")
            else:
                dt_utc = dt.astimezone(timezone.utc)
                if dt_utc.utcoffset() != timezone.utc.utcoffset(dt_utc):
                    reasons.append("date is not UTC")


        except ValueError:
            # iso string itself is invalid
            reasons.append("date parse failed")

    record["invalid_reason"].extend(reasons)
    if len(reasons) > 0:
        record["is_valid"] = False
        # Set shift_log_id to None to avoid duplicate IDs caused by variations in date formatting
        record["shift_log_id"] = None 

    return record


def check_duplicate(record, seen_records):
    """Check duplicate based on date, shift, and line."""

    record_date = record.get("date")
    shift = record.get("shift")
    line = record.get("line")

    if not record_date or not shift or not line:
        return record, seen_records

    duplicate_key = (record_date, shift, line)

    if duplicate_key in seen_records:
        record["is_valid"] = False
        record["invalid_reason"].append(
            "Duplicate record based on date, shift, and line"
        )
        record["is_duplicate"] = True
    else:
        seen_records.add(duplicate_key)

    return record, seen_records


def parse_int(value, field_name, record):
    if value is None or value == "":
        record["is_valid"] = False
        record["invalid_reason"].append(f"{field_name} is missing")
        return None

    try:
        return int(value)
    except (TypeError, ValueError):
        record["is_valid"] = False
        record["invalid_reason"].append(f"{field_name} is not a valid integer")
        return None


def validate_records(records):
    """
    Validate manufacturing shift log records.
    
    validation rules:
    date is not null and can be converted into an ISO format
    duplicate key = date + shift + line
    planned_output > 0
    actual_output >= 0
    defect_qty >= 0
    defect_qty <= actual_output
    downtime_min >= 0
    downtime_min <= 480
    shift in A/B/C
    line is not null
    
    """

    seen_records = set()

    for record in records:
        record["is_valid"] = True
        record["invalid_reason"] = []
        record["is_duplicate"] = False

        # Validate date and date_iso
        record = validate_record_date(record)
        # Check duplicate by date, shift, and line
        record, seen_records = check_duplicate(record, seen_records)

        # Check if the string columns can be converted to numbers
        planned_output = parse_int(record.get("planned_output"), "planned_output", record)
        actual_output = parse_int(record.get("actual_output"), "actual_output", record)
        defect_qty = parse_int(record.get("defect_qty"), "defect_qty", record)
        downtime_min = parse_int(record.get("downtime_min"), "downtime_min", record)

        # Update as numeric
        record["planned_output"] = planned_output
        record["actual_output"] = actual_output
        record["defect_qty"] = defect_qty
        record["downtime_min"] = downtime_min

        shift = record.get("shift")
        line = record.get("line")

        # Validate business rules
        if planned_output is None or planned_output <= 0:
            record["is_valid"] = False
            record["invalid_reason"].append("planned_output is missing or 0 or less")

        if actual_output is None or actual_output < 0:
            record["is_valid"] = False
            record["invalid_reason"].append("actual_output is missing or less than 0")

        if defect_qty is None or defect_qty < 0:
            record["is_valid"] = False
            record["invalid_reason"].append("defect_qty is missing or less than 0")

        if actual_output is not None and defect_qty is not None and defect_qty > actual_output:
            record["is_valid"] = False
            record["invalid_reason"].append("defect_qty is greater than actual_output")

        if downtime_min is None or downtime_min < 0:
            record["is_valid"] = False
            record["invalid_reason"].append("downtime_min is missing or less than 0")

        if downtime_min is not None and downtime_min > 480:
            record["is_valid"] = False
            record["invalid_reason"].append("downtime_min is over 480")

        if shift not in ("A", "B", "C"):
            record["is_valid"] = False
            record["invalid_reason"].append("shift is not A, B, or C")

        if not line:
            record["is_valid"] = False
            record["invalid_reason"].append("line is missing")

        record["invalid_reason"] = sorted(set(record["invalid_reason"]))

    return records