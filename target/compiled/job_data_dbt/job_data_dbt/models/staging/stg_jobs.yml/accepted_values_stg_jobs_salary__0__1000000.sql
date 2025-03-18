
    
    

with all_values as (

    select
        salary as value_field,
        count(*) as n_records

    from `trans-envoy-314612`.`job_data`.`stg_jobs`
    group by salary

)

select *
from all_values
where value_field not in (
    '0','1000000'
)


