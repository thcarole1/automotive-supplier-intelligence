SELECT
    s.supplier_id,
    s.supplier_code,
    s.supplier_name,
    s.risk_profile,
    otd.otd_weighted_by_criticality,
    rank.ppm_score,
    rank.lead_time_score,
    ROUND(
        (100 * (
            {{ var('health_score_kpi_weights')['otd'] }} * COALESCE(otd.otd_weighted_by_criticality, 0)
            + {{ var('health_score_kpi_weights')['ppm'] }} * COALESCE(rank.ppm_score, 0)
            + {{ var('health_score_kpi_weights')['lead_time'] }} * COALESCE(rank.lead_time_score, 0)
        ))::numeric, 1
    ) AS health_score
FROM {{ ref('dim_supplier') }} AS s
LEFT JOIN {{ ref('int_supplier_otd_by_criticality') }} AS otd ON s.supplier_id = otd.supplier_id
LEFT JOIN {{ ref('int_supplier_risk_ranking') }} AS rank ON s.supplier_id = rank.supplier_id
WHERE s.is_current
