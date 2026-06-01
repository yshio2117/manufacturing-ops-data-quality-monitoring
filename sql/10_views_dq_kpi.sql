-- basic metrics by run and source file, including breakdown of invalid reasons
CREATE OR REPLACE VIEW `{PROJECT_ID}.{DATASET_ID}.v_dq_metrics_by_run` AS
WITH base AS (
  SELECT
    run_id,
    source_file,
    ingested_at,
    is_valid,
    is_duplicate,
    IFNULL(invalid_reason, []) AS invalid_reason
  FROM `{SHIFT_LOG_VALIDATED_TABLE_ID}` -- Use the non-deduped table to aggregate duplicates
),
reason_flags AS (
  SELECT
    run_id,
    source_file,
    ingested_at,
    is_valid,
    is_duplicate,
    invalid_reason,

    ('date, shift, or line is missing for shift_log_id generation'
      IN UNNEST(invalid_reason)) AS r_missing_id_fields,

    ('Duplicate record based on date, shift, and line'
      IN UNNEST(invalid_reason)) AS r_duplicate,

    ('planned_output is missing'
      IN UNNEST(invalid_reason)) AS r_planned_output_missing,

    ('planned_output is not a valid integer'
      IN UNNEST(invalid_reason)) AS r_planned_output_parse_failed,

    ('planned_output is 0 or less'
      IN UNNEST(invalid_reason)) AS r_planned_output_invalid,

    ('actual_output is missing'
      IN UNNEST(invalid_reason)) AS r_actual_output_missing,

    ('actual_output is not a valid integer'
      IN UNNEST(invalid_reason)) AS r_actual_output_parse_failed,

    ('actual_output is less than 0'
      IN UNNEST(invalid_reason)) AS r_actual_output_invalid,

    ('defect_qty is missing'
      IN UNNEST(invalid_reason)) AS r_defect_qty_missing,

    ('defect_qty is not a valid integer'
      IN UNNEST(invalid_reason)) AS r_defect_qty_parse_failed,

    ('defect_qty is less than 0'
      IN UNNEST(invalid_reason)) AS r_defect_qty_invalid,

    ('defect_qty is greater than actual_output'
      IN UNNEST(invalid_reason)) AS r_defect_exceeds_actual,

    ('downtime_min is missing'
      IN UNNEST(invalid_reason)) AS r_downtime_missing,

    ('downtime_min is not a valid integer'
      IN UNNEST(invalid_reason)) AS r_downtime_parse_failed,

    ('downtime_min is less than 0'
      IN UNNEST(invalid_reason)) AS r_downtime_negative,

    ('downtime_min is over 480'
      IN UNNEST(invalid_reason)) AS r_downtime_over_480,

    ('shift is not A, B, or C'
      IN UNNEST(invalid_reason)) AS r_invalid_shift,

    ('line is missing'
      IN UNNEST(invalid_reason)) AS r_missing_line

  FROM base
)

SELECT
  run_id,
  source_file,

  MIN(ingested_at) AS run_started_at,
  MAX(ingested_at) AS run_last_seen_at,

  COUNT(*) AS total_rows,
  COUNTIF(is_valid IS TRUE) AS rows_valid,
  COUNTIF(is_valid IS FALSE) AS rows_invalid,
  SAFE_DIVIDE(COUNTIF(is_valid IS TRUE), COUNT(*)) AS valid_rate,

  COUNTIF(NOT r_duplicate AND NOT r_missing_id_fields) AS unique_shift_logs,

  COUNTIF(r_missing_id_fields) AS missing_id_field_rows,
  COUNTIF(r_invalid_shift) AS invalid_shift_rows,
  COUNTIF(r_missing_line) AS missing_line_rows,

  COUNTIF(r_planned_output_missing) AS planned_output_missing_rows,
  COUNTIF(r_planned_output_parse_failed) AS planned_output_parse_failed_rows,
  COUNTIF(r_planned_output_invalid) AS planned_output_invalid_rows,

  COUNTIF(r_actual_output_missing) AS actual_output_missing_rows,
  COUNTIF(r_actual_output_parse_failed) AS actual_output_parse_failed_rows,
  COUNTIF(r_actual_output_invalid) AS actual_output_invalid_rows,

  COUNTIF(r_defect_qty_missing) AS defect_qty_missing_rows,
  COUNTIF(r_defect_qty_parse_failed) AS defect_qty_parse_failed_rows,
  COUNTIF(r_defect_qty_invalid) AS defect_qty_invalid_rows,
  COUNTIF(r_defect_exceeds_actual) AS defect_exceeds_actual_rows,

  COUNTIF(r_downtime_missing) AS downtime_missing_rows,
  COUNTIF(r_downtime_parse_failed) AS downtime_parse_failed_rows,
  COUNTIF(r_downtime_negative) AS downtime_negative_rows,
  COUNTIF(r_downtime_over_480) AS downtime_over_480_rows,

  COUNTIF(r_duplicate OR is_duplicate IS TRUE) AS duplicate_rows,
  SAFE_DIVIDE(COUNTIF(r_duplicate OR is_duplicate IS TRUE), COUNT(*)) AS duplicate_rate,

  SAFE_DIVIDE(
    COUNTIF(
      r_planned_output_parse_failed
      OR r_actual_output_parse_failed
      OR r_defect_qty_parse_failed
      OR r_downtime_parse_failed
    ),
    COUNT(*)
  ) AS numeric_parse_error_rate

FROM reason_flags
GROUP BY run_id, source_file;



-- Breakdown of invalid reasons
CREATE OR REPLACE VIEW `{PROJECT_ID}.{DATASET_ID}.v_dq_invalid_reasons_by_run` AS
SELECT
  run_id,
  source_file,
  reason AS invalid_reason,
  COUNT(*) AS rows_count
FROM `{SHIFT_LOG_VALIDATED_TABLE_ID}`, -- Use the non-deduped table to get all invalid reasons, including duplicates
UNNEST(invalid_reason) AS reason
GROUP BY run_id, source_file, invalid_reason
ORDER BY run_id, rows_count DESC
;