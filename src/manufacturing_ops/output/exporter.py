import csv
import os
import copy
from google.cloud import bigquery
from google.cloud.exceptions import NotFound
from pathlib import Path
from config.settings import BASE_DIR,WRITE_DISPOSITION,SHIFT_LOG_KPI_VIEW_ID



def export_kpi_records_to_csv(kpi_records, filename):

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
                "production_achievement",
                "defect_rate",
                "downtime_rate",
                "operator",
                "source_system",
                "source_file",
                "row_number",
                "row_id",
                "ingested_at",
                "run_id"
                ]
    with open(BASE_DIR / "data/output/{0}.csv".format(filename), "w", encoding="utf_8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(kpi_records)

    print("Exported kpi records to data/output/{0}.csv".format(filename))



def load_kpi_records_to_bigquery(kpi_records):


    schema = [
        bigquery.SchemaField("shift_log_id", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("date", "DATE", mode="REQUIRED"),
        bigquery.SchemaField("shift", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("line", "STRING", mode="REQUIRED"),

        bigquery.SchemaField("planned_output", "INT64", mode="REQUIRED"),
        bigquery.SchemaField("actual_output", "INT64", mode="REQUIRED"),
        bigquery.SchemaField("defect_qty", "INT64", mode="REQUIRED"),
        bigquery.SchemaField("downtime_min", "INT64", mode="REQUIRED"),
        bigquery.SchemaField("downtime_reason", "STRING"),

        bigquery.SchemaField("production_achievement", "FLOAT64"),
        bigquery.SchemaField("defect_rate", "FLOAT64"),
        bigquery.SchemaField("downtime_rate", "FLOAT64"),

        bigquery.SchemaField("operator", "STRING"),
        bigquery.SchemaField("source_system", "STRING"),

        bigquery.SchemaField("source_file", "STRING"),
        bigquery.SchemaField("row_number", "INT64"),
        bigquery.SchemaField("row_id", "STRING"),
        bigquery.SchemaField("ingested_at", "TIMESTAMP"),
        bigquery.SchemaField("run_id", "STRING"),
    ]

    client = bigquery.Client()

    job_config = bigquery.LoadJobConfig(
        schema=schema,
        create_disposition="CREATE_IF_NEEDED",
        write_disposition=WRITE_DISPOSITION,
        clustering_fields=["shift_log_id"] # cluster by shift_log_id to optimize query performance when joining with shift_log_validated table / shift_log_validated_dedup view.
    )
    # load to kpi table
    load_job = client.load_table_from_json(
        kpi_records,
        SHIFT_LOG_KPI_VIEW_ID,
        job_config=job_config
    )

    load_job.result()
    print(f"Loaded kpi records to : {SHIFT_LOG_KPI_VIEW_ID}.")


def load_kpi_records(kpi_records,args):


    # for local CSV, add suffix to the filename
    filename = Path(args.input_file).stem + "_kpi"

    # to CSV
    if args.output == "local":
        export_kpi_records_to_csv(
                                kpi_records,
                                filename=filename
                                )
    else:            
        load_kpi_records_to_bigquery(
                                kpi_records
                                )


