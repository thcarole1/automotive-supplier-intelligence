WITH temporal_match AS (
    SELECT
        qi.incident_id,
        ds.supplier_key
    FROM {{ ref('stg_quality_incidents') }} AS qi
    LEFT JOIN {{ ref('dim_supplier') }} AS ds
        ON qi.supplier_id = ds.supplier_id
        AND qi.incident_date >= CAST(ds.valid_from AS DATE)
        AND (ds.valid_to IS NULL OR qi.incident_date < CAST(ds.valid_to AS DATE))
),

current_match AS (
    SELECT supplier_id, supplier_key
    FROM {{ ref('dim_supplier') }}
    WHERE is_current
)

SELECT
    qi.incident_id,
    COALESCE(tm.supplier_key, cm.supplier_key) AS supplier_key,
    qi.part_id,
    qi.po_id,
    qi.incident_date,
    qi.incident_type,
    qi.severity,
    qi.quantity_affected
FROM {{ ref('stg_quality_incidents') }} AS qi
LEFT JOIN temporal_match AS tm ON qi.incident_id = tm.incident_id
LEFT JOIN current_match AS cm ON qi.supplier_id = cm.supplier_id
