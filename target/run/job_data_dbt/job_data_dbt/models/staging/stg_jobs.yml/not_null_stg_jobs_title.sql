select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
    



select title
from `trans-envoy-314612`.`job_data`.`stg_jobs`
where title is null



      
    ) dbt_internal_test