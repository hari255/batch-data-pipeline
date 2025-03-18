select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
    



select salary
from `trans-envoy-314612`.`job_data`.`stg_jobs`
where salary is null



      
    ) dbt_internal_test