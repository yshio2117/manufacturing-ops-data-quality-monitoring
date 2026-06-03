





with validation_errors as (

    select
        date, shift, line
    from (select * from `study-382607`.`manufacturing_ops_data_quality_dbt_dev`.`shift_log_validated_dedup` where shift_log_id IS NOT NULL) dbt_subquery
    group by date, shift, line
    having count(*) > 1

)

select *
from validation_errors


