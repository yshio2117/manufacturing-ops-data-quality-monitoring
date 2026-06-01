import csv
import os
from google.cloud import bigquery
from google.cloud.exceptions import NotFound
from pathlib import Path
from config.settings import BASE_DIR,WRITE_DISPOSITION,SHIFT_LOG_VALIDATED_TABLE_ID

def export_validated_records_to_csv(records, filename):
    """ Output validated records data to CSV """ 

    fieldnames = ['date', 'date_iso','shift','line','planned_output','actual_output','defect_qty',
                  'downtime_min','downtime_reason','operator','source_system',
                  'source_file','row_number','row_id','ingested_at','run_id',
                  'is_valid','invalid_reason','is_duplicate','date_iso','shift_log_id']

    with open(BASE_DIR / "data/output/{0}.csv".format(filename), "w", encoding="utf_8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)

    print("Exported validated records to data/output/{0}.csv".format(filename))



def load_validated_records_to_bq(records):
    """    Load validated records data to BigQuery """ 

    print("AAA", records[:1])
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
        bigquery.SchemaField(
            "is_valid", # new field for validated_records
            "BOOL",
            mode="REQUIRED",
            description="Whether the record is valid or not"
            ),
        bigquery.SchemaField(
            "invalid_reason", # new field for validated_records
            "STRING",
            mode="REPEATED",  # list
            description="Reason why the record is invalid"
            ),
        bigquery.SchemaField(
            "is_duplicate", # new field for validated_records
            "BOOL",
            mode="REQUIRED",
            description="Whether the record is duplicate or not"
            ),
        bigquery.SchemaField(
            "date_iso", "TIMESTAMP", # new field for validated_records
            description="date in ISO format in UTC timezone"
            ),
        bigquery.SchemaField(
            "shift_log_id", # new field for validated_records
            "STRING",
            description="Unique ID of the record (generated UUID v5 based on date, shift, and line. If either of them is missing, set shift_log_id to None)"
        ),

    ]

    client = bigquery.Client()

    # main table
    shift_log_validated_table = SHIFT_LOG_VALIDATED_TABLE_ID

    # check if validated table exists
    try: 
        shift_log_validated_table = client.get_table(shift_log_validated_table) 
    except NotFound: 
        # create shift_log_validated_table if not exists
        shift_log_validated_table = bigquery.Table(shift_log_validated_table, schema=schema)
        # Set Partition by date_iso
        #shift_log_validated_table.time_partitioning = bigquery.TimePartitioning(
        #    type_=bigquery.TimePartitioningType.DAY,
        #    field="date_iso",  
        #)
        # set clustering by shift_log_id to optimize query performance when joining with shift_log_kpi table
        shift_log_validated_table.clustering_fields = ["shift_log_id"]
        client.create_table(shift_log_validated_table)
        print(f"Created {SHIFT_LOG_VALIDATED_TABLE_ID}.")


    job_config = bigquery.LoadJobConfig(
        schema=schema,
        write_disposition=WRITE_DISPOSITION
    )
        
    # load to validated table
    load_job = client.load_table_from_json(
        records,
        shift_log_validated_table,
        job_config=job_config
    )

    load_job.result()
    print(f"Loaded validated records to : {shift_log_validated_table}.")



def load_validated_records(validated_records, args, suffix="_validated"):
    """ Load validated records to BigQuery or local CSV based on args.output."""

    # for local CSV, add suffix to the filename 
    filename = Path(args.input_file).stem + f"{suffix}"

    if args.output == "bigquery":
        load_validated_records_to_bq(validated_records)
    elif args.output == "local":
        export_validated_records_to_csv(validated_records, filename)
    else:
        raise ValueError(f"Invalid output: {args.output}. Supported outputs are 'bigquery' and 'local'.")

