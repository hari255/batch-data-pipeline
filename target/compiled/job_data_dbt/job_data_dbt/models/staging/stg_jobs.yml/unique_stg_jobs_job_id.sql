
    
    

with dbt_test__target as (

  select job_id as unique_field
  from `trans-envoy-314612`.`job_data`.`stg_jobs`
  where job_id is not null

)

select
    unique_field,
    count(*) as n_records

from dbt_test__target
group by unique_field
having count(*) > 1


