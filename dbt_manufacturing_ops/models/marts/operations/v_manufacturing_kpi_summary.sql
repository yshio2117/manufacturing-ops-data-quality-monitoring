{{ config(materialized='view') }}

SELECT
  COUNT(*) AS kpi_records,
  SUM(planned_output) AS total_planned_output,
  SUM(actual_output) AS total_actual_output,
  SUM(defect_qty) AS total_defects,
  SUM(downtime_min) AS total_downtime_min,
  SAFE_DIVIDE(SUM(actual_output), SUM(planned_output)) AS production_achievement,
  SAFE_DIVIDE(SUM(defect_qty), SUM(actual_output)) AS defect_rate,
  SAFE_DIVIDE(SUM(downtime_min), COUNT(*) * 480) AS downtime_rate
FROM {{ ref('shift_log_kpi') }}