WITH otd_by_criticality AS (
    SELECT
        ds.supplier_id,
        dp.criticality,
        COUNT(*) FILTER (WHERE fd.actual_delivery_date IS NOT NULL) AS total_delivered,
        COUNT(*) FILTER (WHERE fd.is_on_time) AS total_on_time
    FROM {{ ref('fct_delivery') }} AS fd
    JOIN {{ ref('dim_supplier') }} AS ds ON fd.supplier_key = ds.supplier_key
    JOIN {{ ref('dim_part') }} AS dp ON fd.part_id = dp.part_id
    GROUP BY ds.supplier_id, dp.criticality
),

otd_ratios AS (
    SELECT
        supplier_id,
        criticality,
        1.0 * total_on_time / NULLIF(total_delivered, 0) AS otd_ratio
    FROM otd_by_criticality
)

SELECT
    supplier_id,
    SUM(
        COALESCE(otd_ratio, 0) *
        CASE criticality
            WHEN 'LOW' THEN {{ var('health_score_criticality_weights')['LOW'] }}
            WHEN 'MEDIUM' THEN {{ var('health_score_criticality_weights')['MEDIUM'] }}
            WHEN 'HIGH' THEN {{ var('health_score_criticality_weights')['HIGH'] }}
        END
    ) AS otd_weighted_by_criticality
FROM otd_ratios
GROUP BY supplier_id
