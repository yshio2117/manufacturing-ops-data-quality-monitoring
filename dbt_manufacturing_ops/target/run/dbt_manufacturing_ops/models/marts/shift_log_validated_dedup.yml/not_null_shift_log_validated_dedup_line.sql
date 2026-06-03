
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select line
from `study-382607`.`manufacturing_ops_data_quality_dbt_dev`.`shift_log_validated_dedup`
where line is null



  
  
      
    ) dbt_internal_test