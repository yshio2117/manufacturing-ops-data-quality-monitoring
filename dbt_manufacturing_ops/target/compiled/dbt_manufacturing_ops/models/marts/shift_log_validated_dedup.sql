

WITH source_data AS (
    SELECT *
    FROM `study-382607`.`manufacturing_ops_data_quality`.`shift_log_validated`
),
valid_dedup AS (
    SELECT *
    FROM source_data
    WHERE shift_log_id IS NOT NULL
    QUALIFY ROW_NUMBER() OVER(
        PARTITION BY shift_log_id
        ORDER BY ingested_at DESC, row_id DESC
    ) = 1
),

invalid_all AS (
    SELECT *
    FROM source_data
    WHERE shift_log_id IS NULL
)

SELECT * FROM valid_dedup
UNION ALL
SELECT * FROM invalid_all