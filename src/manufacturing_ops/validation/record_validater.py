from datetime import datetime, date, timezone, timedelta


def validate_record_date(record):
    """
    Validate raw date and normalized production_date.

    Rules:
    1. If raw date is missing -> invalid
    2. If raw date exists but production_date is None -> invalid
    3. If production_date exists but is not YYYY-MM-DD -> invalid
    """

    reasons = record.get("invalid_reason", [])

    raw_date = record.get("date")
    production_date = record.get("production_date")

    # Check if date is missing
    raw_is_missing = (
        raw_date is None 
        or not isinstance(raw_date, str) # not a string type
        or not raw_date.strip() # contains only whitespace
    )

    if raw_is_missing:
        reasons.append("date is missing")

    if not raw_is_missing and production_date is None:
        reasons.append("date parse failed")

    if production_date is not None:
        try:
            datetime.strptime(production_date, "%Y-%m-%d").date()
        except (TypeError, ValueError):
            reasons.append("production_date is invalid")

    record["invalid_reason"] = reasons

    if reasons:
        record["is_valid"] = False

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



def validate_records(records):
    """
    Validate manufacturing shift log records.
    
    validation rules:
    date is not null and can be converted into YYYY-MM-DD format
    duplicate key = date + shift + line
    planned_output_int > 0
    actual_output_int >= 0
    defect_qty_int >= 0
    defect_qty_int <= actual_output_int
    downtime_min_int >= 0
    downtime_min_int <= 480
    shift_normalized in A/B/C
    line_normalized is not null
    
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

        # Validate normalized/parsed fields
        planned_output = record.get("planned_output_int")
        actual_output = record.get("actual_output_int")
        defect_qty = record.get("defect_qty_int")
        downtime_min = record.get("downtime_int")
        shift = record.get("shift_normalized")
        line = record.get("line_normalized")

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