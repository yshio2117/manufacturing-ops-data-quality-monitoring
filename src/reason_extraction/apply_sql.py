import os
from pathlib import Path
from google.cloud import bigquery
from config.settings import PROJECT_ID,DATASET_ID,SHIFT_LOG_VALIDATED_TABLE_ID,SHIFT_LOG_VALIDATED_DEDUP_VIEW_ID,SHIFT_LOG_KPI_VIEW_ID


def render_sql(template):
    return template.format(PROJECT_ID=PROJECT_ID, 
                           DATASET_ID=DATASET_ID,
                           SHIFT_LOG_VALIDATED_TABLE_ID=SHIFT_LOG_VALIDATED_TABLE_ID,
                           SHIFT_LOG_VALIDATED_DEDUP_VIEW_ID=SHIFT_LOG_VALIDATED_DEDUP_VIEW_ID,
                           SHIFT_LOG_KPI_VIEW_ID=SHIFT_LOG_KPI_VIEW_ID
                           )

def run_sql_file(client, path):
    template = path.read_text(encoding="utf-8")
    sql = render_sql(template)
    job = client.query(sql)
    job.result()

def main():
    client = bigquery.Client()
    for p in sorted(Path("sql").glob("*.sql")):
        print(f"Running: {p}")
        run_sql_file(client, p)

if __name__ == "__main__":
    main()