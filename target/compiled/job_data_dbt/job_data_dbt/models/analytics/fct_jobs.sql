WITH jobs AS (
    SELECT * FROM `trans-envoy-314612`.`job_data`.`stg_jobs`
),  
unnested_jobs AS (
    SELECT 
        job.id AS job_id,
        job.title AS title,
        job.company_name AS company,
        job.location AS location,
        job.type AS employment_type,
        SAFE_CAST(job.description.salaryRangeMaxYearly AS FLOAT64) AS salary_max,
        SAFE_CAST(job.description.salaryRangeMinYearly AS FLOAT64) AS salary_min,
        TIMESTAMP(job.created_at) AS created_at
    FROM jobs, UNNEST(jobs) AS job  -- Correct BigQuery syntax
)
SELECT 
    job_id,
    title,
    company,
    location,
    employment_type,
    salary_min,
    salary_max,
    created_at,
    CASE 
        WHEN salary_max IS NULL THEN 'Unknown'
        WHEN salary_max < 50000 THEN 'Low'
        WHEN salary_max BETWEEN 50000 AND 100000 THEN 'Medium'
        ELSE 'High'
    END AS salary_category
FROM unnested_jobs  -- 🚀 Removed the semicolon here!