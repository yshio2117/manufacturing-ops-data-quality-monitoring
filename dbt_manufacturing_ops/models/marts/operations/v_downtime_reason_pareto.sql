{{ config(materialized='view') }}

WITH reason_totals AS (
  SELECT
    downtime_reason,
    SUM(downtime_min) AS total_downtime_min
  FROM {{ ref('shift_log_kpi') }}
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
ORDER BY total_downtime_min DESC