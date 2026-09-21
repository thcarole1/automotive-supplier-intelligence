WITH stock_bounds AS (
    SELECT
        part_id,
        MIN(snapshot_date) AS first_date,
        MAX(snapshot_date) AS last_date,
        (ARRAY_AGG(stock_quantity ORDER BY snapshot_date ASC))[1] AS initial_stock,
        (ARRAY_AGG(stock_quantity ORDER BY snapshot_date DESC))[1] AS final_stock,
        (ARRAY_AGG(safety_stock ORDER BY snapshot_date DESC))[1] AS safety_stock
    FROM {{ ref('fct_inventory_snapshot') }}
    GROUP BY part_id
),

deliveries_received AS (
    SELECT
        part_id,
        SUM(quantity_delivered) AS total_received
    FROM {{ ref('fct_delivery') }}
    WHERE actual_delivery_date IS NOT NULL
    GROUP BY part_id
),

daily_consumption AS (
    SELECT
        sb.part_id,
        sb.last_date AS as_of_date,
        sb.final_stock AS stock_quantity,
        sb.safety_stock,
        (sb.initial_stock + COALESCE(dr.total_received, 0) - sb.final_stock)
            / NULLIF(sb.last_date - sb.first_date, 0)::numeric AS avg_daily_consumption
    FROM stock_bounds AS sb
    LEFT JOIN deliveries_received AS dr ON sb.part_id = dr.part_id
)

SELECT
    p.part_id,
    p.part_code,
    p.family,
    p.criticality,
    dc.as_of_date,
    dc.stock_quantity,
    dc.safety_stock,
    ROUND(dc.avg_daily_consumption, 2) AS avg_daily_consumption,
    ROUND(dc.stock_quantity / NULLIF(dc.avg_daily_consumption, 0), 1) AS days_of_supply
FROM {{ ref('dim_part') }} AS p
JOIN daily_consumption AS dc ON p.part_id = dc.part_id
