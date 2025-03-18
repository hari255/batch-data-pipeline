SELECT 
    job.id AS job_id,
    job.title AS title,
    job.company_name AS company,
    job.location AS location,
    job.type AS employment_type,
    SAFE_CAST(job.description.salaryRangeMaxYearly AS FLOAT64) AS salary_max,
    SAFE_CAST(job.description.salaryRangeMinYearly AS FLOAT64) AS salary_min,
    TIMESTAMP(job.created_at) AS created_at
FROM `trans-envoy-314612.job_data.staging_jobs`,
UNNEST(jobs) AS job