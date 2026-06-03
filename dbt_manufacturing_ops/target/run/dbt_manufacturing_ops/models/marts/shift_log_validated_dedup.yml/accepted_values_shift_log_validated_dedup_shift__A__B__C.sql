
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    

with all_values as (

    select
        shift as value_field,
        count(*) as n_records

    from `study-382607`.`manufacturing_ops_data_quality_dbt_dev`.`shift_log_validated_dedup`
    group by shift

)

select *
from all_values
where value_field not in (
    'A','B','C'
)



  
  
      
    ) dbt_internal_test