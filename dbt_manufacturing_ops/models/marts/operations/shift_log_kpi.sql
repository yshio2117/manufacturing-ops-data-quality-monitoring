{{ config(materialized='view') }}

SELECT
  shift_log_id,
  date,
  shift,
  line,
  planned_output,
  actual_output,
  defect_qty,
  downtime_min,
  downtime_reason,
  operator,
  source_system,
  source_file,
  row_number,
  row_id,
  run_id,
  ingested_at,

  SAFE_DIVIDE(actual_output, planned_output) AS production_achievement,
  SAFE_DIVIDE(defect_qty, actual_output) AS defect_rate,
  SAFE_DIVIDE(downtime_min, 480) AS downtime_rate
FROM {{ ref('shift_log_validated_dedup') }}
WHERE is_valid IS TRUE