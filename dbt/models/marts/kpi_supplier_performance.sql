WITH deliveries_agg AS (
    SELECT
        ds.supplier_id,
        COUNT(*) FILTER (WHERE fd.actual_delivery_date IS NOT NULL) AS total_delivered,
        COUNT(*) FILTER (WHERE fd.is_on_time) AS total_on_time,
        SUM(fd.quantity_delivered) AS total_quantity_delivered
    FROM {{ ref('fct_delivery') }} AS fd
    JOIN {{ ref('dim_supplier') }} AS ds ON fd.supplier_key = ds.supplier_key
    GROUP BY ds.supplier_id
),

incidents_agg AS (
    SELECT
        ds.supplier_id,
        SUM(fqi.quantity_affected) AS total_quantity_affected
    FROM {{ ref('fct_quality_incident') }} AS fqi
    JOIN {{ ref('dim_supplier') }} AS ds ON fqi.supplier_key = ds.supplier_key
    GROUP BY ds.supplier_id
),

lead_time_agg AS (
    SELECT
        ds.supplier_id,
        AVG(fd.actual_delivery_date - fpol.order_date) AS lead_time_avg_days,
        STDDEV(fd.actual_delivery_date - fpol.order_date) AS lead_time_stddev_days
    FROM {{ ref('fct_delivery') }} AS fd
    JOIN {{ ref('fct_purchase_order_line') }} AS fpol ON fd.po_id = fpol.po_id
    JOIN {{ ref('dim_supplier') }} AS ds ON fd.supplier_key = ds.supplier_key
    WHERE fd.actual_delivery_date IS NOT NULL
    GROUP BY ds.supplier_id
)

SELECT
    s.supplier_id,
    s.supplier_code,
    s.supplier_name,
    s.risk_profile,
    ROUND(1.0 * da.total_on_time / NULLIF(da.total_delivered, 0), 4) AS otd_ratio,
    ROUND(1000000.0 * COALESCE(ia.total_quantity_affected, 0) / NULLIF(da.total_quantity_delivered, 0), 2) AS ppm,
    lt.lead_time_avg_days,
    lt.lead_time_stddev_days
FROM {{ ref('dim_supplier') }} AS s
LEFT JOIN deliveries_agg AS da ON s.supplier_id = da.supplier_id
LEFT JOIN incidents_agg AS ia ON s.supplier_id = ia.supplier_id
LEFT JOIN lead_time_agg AS lt ON s.supplier_id = lt.supplier_id
WHERE s.is_current
