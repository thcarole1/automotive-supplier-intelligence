WITH bounds AS (
    SELECT
        part_id,
        MAX(snapshot_date) AS last_date
    FROM {{ ref('fct_inventory_snapshot') }}
    GROUP BY part_id
),

latest AS (
    SELECT
        fis.part_id,
        fis.snapshot_date AS as_of_date,
        fis.stock_quantity,
        fis.safety_stock
    FROM {{ ref('fct_inventory_snapshot') }} AS fis
    JOIN bounds AS b ON fis.part_id = b.part_id AND fis.snapshot_date = b.last_date
),

window_start_stock AS (
    SELECT
        fis.part_id,
        fis.stock_quantity AS stock_at_window_start
    FROM {{ ref('fct_inventory_snapshot') }} AS fis
    JOIN bounds AS b ON fis.part_id = b.part_id
    WHERE fis.snapshot_date = b.last_date - {{ var('days_of_supply_window_days') }}
),

deliveries_in_window AS (
    SELECT
        fd.part_id,
        SUM(fd.quantity_delivered) AS total_received
    FROM {{ ref('fct_delivery') }} AS fd
    JOIN bounds AS b ON fd.part_id = b.part_id
    WHERE fd.actual_delivery_date IS NOT NULL
        AND fd.actual_delivery_date > b.last_date - {{ var('days_of_supply_window_days') }}
        AND fd.actual_delivery_date <= b.last_date
    GROUP BY fd.part_id
),

recent_consumption AS (
    SELECT
        ws.part_id,
        GREATEST(
            (ws.stock_at_window_start + COALESCE(dw.total_received, 0) - l.stock_quantity)
                / {{ var('days_of_supply_window_days') }}::numeric,
            0.01
        ) AS avg_daily_consumption
    FROM window_start_stock AS ws
    JOIN latest AS l ON ws.part_id = l.part_id
    LEFT JOIN deliveries_in_window AS dw ON ws.part_id = dw.part_id
)

SELECT
    p.part_id,
    p.part_code,
    p.family,
    p.criticality,
    l.as_of_date,
    l.stock_quantity,
    l.safety_stock,
    ROUND(rc.avg_daily_consumption, 2) AS avg_daily_consumption,
    ROUND(l.stock_quantity / rc.avg_daily_consumption, 1) AS days_of_supply
FROM {{ ref('dim_part') }} AS p
JOIN latest AS l ON p.part_id = l.part_id
JOIN recent_consumption AS rc ON p.part_id = rc.part_id
