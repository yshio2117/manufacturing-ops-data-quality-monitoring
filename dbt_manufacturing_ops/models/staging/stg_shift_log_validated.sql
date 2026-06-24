{{ config(materialized='view') }}

WITH source AS (

    SELECT *
    FROM {{ source('shift_log', 'validated') }}

),

renamed AS (

    SELECT
        row_id,
        shift_log_id,

        date,
        shift_normalized AS shift,
        line_normalized AS line,

        planned_output_int AS planned_output,
        actual_output_int AS actual_output,
        defect_qty_int AS defect_qty,
        downtime_min_int AS downtime_min,

        downtime_reason,
        operator,
        source_system,

        is_valid,
        invalid_reason,
        is_duplicate,

        ingested_at,
        source_file,
        row_number,
        run_id

    FROM source

)

SELECT *
FROM renamed