import csv
import os
import sys
import uuid
from datetime import datetime,timezone
from zoneinfo import ZoneInfo
from google.cloud import bigquery
from google.cloud.exceptions import NotFound
from pathlib import Path
from config.settings import BASE_DIR,WRITE_DISPOSITION,PROJECT_ID,DATASET_ID,SHIFT_LOG_RAW_TABLE_ID



def make_run_id(prefix="records"):
    """
    Generate a run ID with the format: {prefix}_{timestamp}_{random}, where:
    - prefix: a string prefix for the run ID (default: "records")
    - timestamp: current UTC time in the format YYYYMMDDTHHMMSSZ
    - random: a random 8-character hexadecimal string
    """

    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    rand = uuid.uuid4().hex[:8]
    return f"{prefix}_{ts}_{rand}"


def read_records_csv_with_metadata(args):

    """
    Read a CSV and add ingestion metadata columns:
      - source_file: the input file name (as string)
      - row_number:  1-based row number within the CSV (excluding header)
      - ingested_at: UTC timestamp when this function was called (batch timestamp)
      - row_id:      UUID v4 per row (string)

    Returns:
      List of dictionaries (one per row)
    """

    file_path = args.input_file

    with open(BASE_DIR / "{0}".format(file_path), "r", encoding="utf_8", newline="") as f:
        reader = csv.DictReader(f)

        source_file = Path(file_path).name
        ingested_at = datetime.now(timezone.utc).isoformat(timespec='seconds')
        if args.run_id:
            run_id = args.run_id
        else:
            run_id = make_run_id()

        rows = []

        for idx, row in enumerate(reader, start=1):
            new_row = {
                "source_file": source_file,
                "row_number": idx,
                "ingested_at": ingested_at,
                "row_id": str(uuid.uuid4()),
                "run_id": run_id,
            }

            # add the original row data to the new row
            new_row.update(row)

            rows.append(new_row)

    return rows


def raw_records_to_csv(records, filename):
    """
    Output raw records data to CSV
    Parameter
    ----------
    records : list of dict
          [{'date','shift,line','planned_output','actual_output','defect_qty',
            'downtime_min','downtime_reason','operator','source_system','source_file','row_number','row_id','ingested_at','run_id'}, ...]       
    filename : str
        output filename
    Returns
    -------
    None

    """ 


    fieldnames = ['date','shift', 'line','planned_output','actual_output','defect_qty',
                  'downtime_min','downtime_reason','operator','source_system',
                  'source_file','row_number','row_id','ingested_at','run_id']

    with open(BASE_DIR / "data/output/{0}.csv".format(filename), "w", encoding="utf_8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)

    print("Exported raw records to data/output/{0}.csv".format(filename))
    
   
def raw_records_to_bq(records):
    """
    Load raw records to BigQuery 

    ----------
    records : list of dict
             [{'date','shift,line','planned_output','actual_output','defect_qty',
               'downtime_min','downtime_reason','operator','source_system','row_number','row_id','ingested_at','run_id'}, ...]       

    Returns
    -------
    None

    """ 


    schema = [
        bigquery.SchemaField(
            "date",
            "DATE",
            description="Production date"
        ),
        bigquery.SchemaField(
            "shift",
            "STRING",
            description="Production shift (A, B, C)"
        ),
        bigquery.SchemaField(
            "line",
            "STRING",
            description="Production line"
        ),
        bigquery.SchemaField(
            "planned_output",
            "INT64",
            description="Planned production quantity"
        ),
        bigquery.SchemaField(
            "actual_output",
            "INT64",
            description="Actual production quantity"
        ),
        bigquery.SchemaField(
            "defect_qty",
            "INT64",
            description="Defective quantity"
        ),
        bigquery.SchemaField(
            "downtime_min",
            "INT64",
            description="Downtime in minutes"
        ),
        bigquery.SchemaField(
            "downtime_reason",
            "STRING",
            description="Reason for downtime"
        ),
        bigquery.SchemaField(
            "operator",
            "STRING",
            description="Shift operator"
        ),
        bigquery.SchemaField(
            "source_system",
            "STRING",
            description="Source system of the shift log"
        ),
        bigquery.SchemaField(
            "source_file",
            "STRING",
            mode="REQUIRED",
            description="Source file name"
        ),
        bigquery.SchemaField(
            "row_number",
            "INT64",
            mode="REQUIRED",
            description="Row number in source file"
        ),
        bigquery.SchemaField(
            "row_id",
            "STRING",
            mode="REQUIRED",
            description="Unique row UUID"
        ),
        bigquery.SchemaField(
            "ingested_at",
            "TIMESTAMP",
            mode="REQUIRED",
            description="Ingestion timestamp"
        ),
        bigquery.SchemaField(
            "run_id",
            "STRING",
            mode="REQUIRED",
            description="Pipeline execution ID"
        ),
    ]

    client = bigquery.Client()

    # check if dataset exists, if not create it
    dataset_ref = PROJECT_ID + "." + DATASET_ID
    
    try:
        client.get_dataset(dataset_ref)
        print(f"Dataset exists: {dataset_ref}")
    except NotFound:
        print(f"Dataset {dataset_ref} not found. Creating...")
        dataset = bigquery.Dataset(dataset_ref)
        dataset.location = "US"
        client.create_dataset(dataset)
        print(f"Dataset {dataset_ref} created.")

    # load data to BigQuery, if the table doesn't exist, create it with the defined schema
    try:
        client.get_table(SHIFT_LOG_RAW_TABLE_ID)
    except NotFound:
        client.create_table(bigquery.Table(SHIFT_LOG_RAW_TABLE_ID, schema=schema))
        print(f"Created {SHIFT_LOG_RAW_TABLE_ID}.")

    job_config = bigquery.LoadJobConfig(
        schema=schema,
        write_disposition=WRITE_DISPOSITION
    )

    load_job = client.load_table_from_json(
        records,
        SHIFT_LOG_RAW_TABLE_ID,
        job_config=job_config
    )

    load_job.result()
    print(f"Loaded raw records to: {SHIFT_LOG_RAW_TABLE_ID}.")


def load_raw_records(records, args, suffix):

    # for local CSV, add suffix to the filename 
    filename = Path(args.input_file).stem + f"{suffix}"
    if args.output == "local":
        # export to local
        raw_records_to_csv(records, filename)
    else:
        # export to BigQuery
        raw_records_to_bq(records)