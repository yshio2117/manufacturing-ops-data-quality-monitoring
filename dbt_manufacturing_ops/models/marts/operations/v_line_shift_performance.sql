{{ config(materialized='view') }}

SELECT
  line,
  shift,
  COUNT(*) AS shift_count,
  SUM(planned_output) AS planned_output,
  SUM(actual_output) AS actual_output,
  SUM(defect_qty) AS defect_qty,
  SUM(downtime_min) AS downtime_min,
  SAFE_DIVIDE(SUM(actual_output), SUM(planned_output)) AS production_achievement,
  SAFE_DIVIDE(SUM(defect_qty), SUM(actual_output)) AS defect_rate,
  SAFE_DIVIDE(SUM(downtime_min), COUNT(*) * 480) AS downtime_rate
FROM {{ ref('shift_log_kpi') }}
GROUP BY line, shift