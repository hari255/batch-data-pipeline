select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
    



select job_id
from `trans-envoy-314612`.`job_data`.`stg_jobs`
where job_id is null



      
    ) dbt_internal_test