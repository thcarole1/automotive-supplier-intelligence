WITH base_kpis AS (
    SELECT
        supplier_id,
        ppm,
        lead_time_stddev_days
    FROM {{ ref('kpi_supplier_performance') }}
)

SELECT
    supplier_id,
    ppm,
    lead_time_stddev_days,
    1.0 - PERCENT_RANK() OVER (ORDER BY ppm ASC) AS ppm_score,
    1.0 - PERCENT_RANK() OVER (ORDER BY lead_time_stddev_days ASC) AS lead_time_score
FROM base_kpis
