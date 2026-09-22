WITH spine AS (
    {{
        dbt_utils.date_spine(
            datepart="day",
            start_date="cast('2023-01-01' as date)",
            end_date="cast('2026-01-01' as date)"
        )
    }}
)

SELECT
    CAST(date_day AS DATE) AS date_day,
    EXTRACT(YEAR FROM date_day) AS year,
    EXTRACT(QUARTER FROM date_day) AS quarter,
    EXTRACT(MONTH FROM date_day) AS month,
    TO_CHAR(date_day, 'Month') AS month_name,
    DATE_TRUNC('month', date_day)::date AS month_start_date,
    EXTRACT(WEEK FROM date_day) AS week_of_year,
    EXTRACT(DOW FROM date_day) AS day_of_week,
    TO_CHAR(date_day, 'Day') AS day_name,
    CASE WHEN EXTRACT(DOW FROM date_day) IN (0, 6) THEN TRUE ELSE FALSE END AS is_weekend
FROM spine
