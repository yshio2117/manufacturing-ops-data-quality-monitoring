from src.reason_extraction.ingestion.record_loader import read_records_csv_with_metadata, load_raw_records
from src.reason_extraction.validation.record_validater import validate_records
from src.reason_extraction.validation.validated_record_loader import load_validated_records
from src.reason_extraction.transformation.record_transformer import add_shift_log_id, to_iso_utc, split_records_by_validity, filter_columns, build_shift_log_kpi_records
from src.reason_extraction.output.exporter import load_kpi_records


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
    
    # Only valid_records for next steps
    #valid_records, invalid_records = split_records_by_validity(validated_records)

    # 4. Curate KPI
    #kpi_records = build_shift_log_kpi_records(valid_records)

    # 5. Load KPI records to BigQuery or local CSV
    #load_kpi_records(kpi_records, args)


