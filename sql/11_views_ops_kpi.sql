-- Curated operational KPI view generated from valid, deduplicated records
CREATE OR REPLACE VIEW `{SHIFT_LOG_KPI_VIEW_ID}` AS
SELECT
  shift_log_id,
  production_date as date,
  shift_normalized as shift,
  line_normalized as line,
  planned_output_int as planned_output,
  actual_output_int as actual_output,
  defect_qty_int as defect_qty,
  downtime_min_int as downtime_min,
  downtime_reason,
  operator,
  source_system,
  source_file,
  row_number,
  row_id,
  run_id,
  ingested_at,

  SAFE_DIVIDE(actual_output_int, planned_output_int) AS production_achievement,
  SAFE_DIVIDE(defect_qty_int, actual_output_int) AS defect_rate,
  SAFE_DIVIDE(downtime_min_int, 480) AS downtime_rate
FROM `{SHIFT_LOG_VALIDATED_DEDUP_VIEW_ID}`
WHERE is_valid IS TRUE;


-- Page 2: Manufacturing KPI summary
CREATE OR REPLACE VIEW `{PROJECT_ID}.{DATASET_ID}.v_manufacturing_kpi_summary` AS
SELECT
  COUNT(*) AS kpi_records,
  SUM(planned_output) AS total_planned_output,
  SUM(actual_output) AS total_actual_output,
  SUM(defect_qty) AS total_defects,
  SUM(downtime_min) AS total_downtime_min,
  SAFE_DIVIDE(SUM(actual_output), SUM(planned_output)) AS production_achievement,
  SAFE_DIVIDE(SUM(defect_qty), SUM(actual_output)) AS defect_rate,
  SAFE_DIVIDE(SUM(downtime_min), COUNT(*) * 480) AS downtime_rate
FROM `{SHIFT_LOG_KPI_VIEW_ID}`;


-- Page 2: Daily KPI trend
CREATE OR REPLACE VIEW `{PROJECT_ID}.{DATASET_ID}.v_manufacturing_kpi_daily_trend` AS
SELECT
  date,
  COUNT(*) AS shift_count,
  SUM(planned_output) AS planned_output,
  SUM(actual_output) AS actual_output,
  SUM(defect_qty) AS defect_qty,
  SUM(downtime_min) AS downtime_min,
  SAFE_DIVIDE(SUM(actual_output), SUM(planned_output)) AS production_achievement,
  SAFE_DIVIDE(SUM(defect_qty), SUM(actual_output)) AS defect_rate,
  SAFE_DIVIDE(SUM(downtime_min), COUNT(*) * 480) AS downtime_rate
FROM `{SHIFT_LOG_KPI_VIEW_ID}`
GROUP BY date;


-- Page 2: KPI by production line
CREATE OR REPLACE VIEW `{PROJECT_ID}.{DATASET_ID}.v_manufacturing_kpi_by_line` AS
SELECT
  line,
  COUNT(*) AS shift_count,
  SUM(planned_output) AS planned_output,
  SUM(actual_output) AS actual_output,
  SUM(defect_qty) AS defect_qty,
  SUM(downtime_min) AS downtime_min,
  SAFE_DIVIDE(SUM(actual_output), SUM(planned_output)) AS production_achievement,
  SAFE_DIVIDE(SUM(defect_qty), SUM(actual_output)) AS defect_rate,
  SAFE_DIVIDE(SUM(downtime_min), COUNT(*) * 480) AS downtime_rate
FROM `{SHIFT_LOG_KPI_VIEW_ID}`
GROUP BY line;


-- Page 2: KPI by shift
CREATE OR REPLACE VIEW `{PROJECT_ID}.{DATASET_ID}.v_manufacturing_kpi_by_shift` AS
SELECT
  shift,
  COUNT(*) AS shift_count,
  SUM(planned_output) AS planned_output,
  SUM(actual_output) AS actual_output,
  SUM(defect_qty) AS defect_qty,
  SUM(downtime_min) AS downtime_min,
  SAFE_DIVIDE(SUM(actual_output), SUM(planned_output)) AS production_achievement,
  SAFE_DIVIDE(SUM(defect_qty), SUM(actual_output)) AS defect_rate,
  SAFE_DIVIDE(SUM(downtime_min), COUNT(*) * 480) AS downtime_rate
FROM `{SHIFT_LOG_KPI_VIEW_ID}`
GROUP BY shift;

-- Page 3: Downtime reason Pareto
CREATE OR REPLACE VIEW `{PROJECT_ID}.{DATASET_ID}.v_downtime_reason_pareto` AS
WITH reason_totals AS (
  SELECT
    downtime_reason,
    SUM(downtime_min) AS total_downtime_min
  FROM `{SHIFT_LOG_KPI_VIEW_ID}`
  GROUP BY downtime_reason
),
reason_shares AS (
  SELECT
    downtime_reason,
    total_downtime_min,
    SAFE_DIVIDE(
      total_downtime_min,
      SUM(total_downtime_min) OVER()
    ) AS downtime_share
  FROM reason_totals
)
SELECT
  downtime_reason,
  total_downtime_min,
  downtime_share,
  SUM(downtime_share) OVER (
    ORDER BY total_downtime_min DESC
    ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
  ) AS cumulative_downtime_share
FROM reason_shares
ORDER BY total_downtime_min DESC;


-- Page 3: Line x shift performance matrix
CREATE OR REPLACE VIEW `{PROJECT_ID}.{DATASET_ID}.v_line_shift_performance` AS
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
FROM `{SHIFT_LOG_KPI_VIEW_ID}`
GROUP BY line, shift;


-- Page 3: Record drilldown
CREATE OR REPLACE VIEW `{PROJECT_ID}.{DATASET_ID}.v_shift_log_kpi_drilldown` AS
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
FROM `{SHIFT_LOG_KPI_VIEW_ID}`;
