from src.manufacturing_ops.ingestion.record_loader import read_records_csv_with_metadata, load_raw_records
from src.manufacturing_ops.validation.record_validater import validate_records
from src.manufacturing_ops.validation.validated_record_loader import load_validated_records
from src.manufacturing_ops.transformation.record_transformer import add_shift_log_id, normalize_records


def run_pipeline(args):
    # 1. Ingestion (read CSV file and file-level validation)
    records = read_records_csv_with_metadata(args)

    # 2. Load raw records to BigQuery or local CSV
    load_raw_records(records, args, suffix="_raw")

    # 3. Normalize fields needed for business keys (production_date, shift, and line) and parse numeric fields.
    records = normalize_records(records)

    # 4. Validation (record-level)
    validated_records = validate_records(records)

    # 5. Add shift_log_id only for valid business keys
    validated_records = add_shift_log_id(validated_records)

    # 6. Load validated_records to BigQuery or local CSV
    load_validated_records(validated_records, args, suffix="_validated") 



