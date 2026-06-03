from src.manufacturing_ops.ingestion.record_loader import read_records_csv_with_metadata, load_raw_records
from src.manufacturing_ops.validation.record_validater import validate_records
from src.manufacturing_ops.validation.validated_record_loader import load_validated_records
from src.manufacturing_ops.transformation.record_transformer import add_shift_log_id, to_iso_utc


def run_pipeline(args):
    # 1. Ingestion (read CSV file and load to BigQuery or local CSV)
    records = read_records_csv_with_metadata(args)

    # Load raw records to BigQuery or local CSV
    load_raw_records(records, args, suffix="_raw")

    # 2. Transformation
    # adding deterministic shift_log_id(uuid v5) if date, shift, and line exist
    records = add_shift_log_id(records)

    # Convert record_date to ISO format in UTC timezone
    records = to_iso_utc(records)

    # 3. Validation 
    validated_records = validate_records(records)

    # Load validated_records to BigQuery or local CSV
    load_validated_records(validated_records, args, suffix="_validated") 



