from pathlib import Path
import os
from google.cloud import bigquery
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv() 

BASE_DIR = Path(__file__).resolve().parents[1]

# which sentiment to extract reasons for, default is negative
SENTIMENT_LABELS = ["negative", "positive"] 


# BigQuery settings
PROJECT_ID = os.getenv("PROJECT_ID")
DATASET_ID = os.getenv("DATASET_ID")
TABLE_PREFIX = os.getenv("TABLE_PREFIX", "customer_feedback")

DBT_TARGET = os.getenv("DBT_TARGET", "dev")
DBT_DATASET_IDS = {
    "dev": os.getenv("DBT_DATASET_ID_DEV"),
    "prod": os.getenv("DBT_DATASET_ID_PROD"),
}
DBT_DATASET_ID = DBT_DATASET_IDS[DBT_TARGET]

def bq_table_id(dataset: str, name: str) -> str:
    return f"{PROJECT_ID}.{dataset}.{name}"

# Output tables
REVIEW_RAW_TABLE_ID = bq_table_id(
    DATASET_ID,
    f"{TABLE_PREFIX}_raw"
)
REVIEW_VALIDATED_TABLE_ID = bq_table_id(
    DATASET_ID,
    f"{TABLE_PREFIX}_validated"
)
REVIEW_REASONS_TABLE_ID = bq_table_id(
    DATASET_ID,
    f"{TABLE_PREFIX}_attributes"
)
REVIEW_VALIDATED_DEDUP_VIEW_ID = bq_table_id(
    DBT_DATASET_ID,
    f"{TABLE_PREFIX}_validated_dedup"
)

# Default: append. Set WRITE_MODE=truncate in GitHub Actions to overwrite the table on each run.
WRITE_MODE = os.getenv("WRITE_MODE", "append")

if WRITE_MODE == "truncate":
    WRITE_DISPOSITION = bigquery.WriteDisposition.WRITE_TRUNCATE
else:
    WRITE_DISPOSITION = bigquery.WriteDisposition.WRITE_APPEND