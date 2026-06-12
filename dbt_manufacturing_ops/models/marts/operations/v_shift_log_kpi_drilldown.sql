{{ config(materialized='view') }}

SELECT
  date,
  shift,
  line,
  planned_output,
  actual_output,
  defect_qty,
  downtime_min,
  downtime_reason,
  production_achievement,
  defect_rate,
  downtime_rate,
  operator,
  source_system,
  source_file,
  row_number,
  row_id,
  run_id,
  ingested_at
FROM {{ ref('shift_log_kpi') }}