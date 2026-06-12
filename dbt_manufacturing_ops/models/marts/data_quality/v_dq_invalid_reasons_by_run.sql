{{ config(materialized='view') }}

SELECT
  run_id,
  source_file,
  reason AS invalid_reason,
  COUNT(*) AS rows_count
FROM {{ ref('stg_shift_log_validated') }}, -- Use the non-deduped table to get all invalid reasons, including duplicates
UNNEST(invalid_reason) AS reason
GROUP BY run_id, source_file, invalid_reason
ORDER BY run_id, rows_count DESC