with source as (

    select *
    from {{ source('pipeline', 'shift_log_validated') }}

),

renamed as (

    select
        row_id,
        shift_log_id,

        date,
        shift_normalized as shift,
        line_normalized as line,

        planned_output_int as planned_output,
        actual_output_int as actual_output,
        defect_qty_int as defect_qty,
        downtime_min_int as downtime_min,

        downtime_reason,
        operator,
        source_system,

        is_valid,
        invalid_reason,
        is_duplicate,

        ingested_at,
        source_file_name,
        pipeline_run_id

    from source

)

select *
from renamed