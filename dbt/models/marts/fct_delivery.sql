WITH temporal_match AS (
    SELECT
        d.delivery_id,
        ds.supplier_key
    FROM {{ ref('int_deliveries_enriched') }} AS d
    LEFT JOIN {{ ref('dim_supplier') }} AS ds
        ON d.supplier_id = ds.supplier_id
        AND d.expected_delivery_date >= CAST(ds.valid_from AS DATE)
        AND (ds.valid_to IS NULL OR d.expected_delivery_date < CAST(ds.valid_to AS DATE))
),

current_match AS (
    SELECT supplier_id, supplier_key
    FROM {{ ref('dim_supplier') }}
    WHERE is_current
)

SELECT
    d.delivery_id,
    d.po_id,
    COALESCE(tm.supplier_key, cm.supplier_key) AS supplier_key,
    d.part_id,
    d.shipment_date,
    d.expected_delivery_date,
    d.actual_delivery_date,
    d.quantity_delivered,
    d.delay_days,
    d.is_on_time
FROM {{ ref('int_deliveries_enriched') }} AS d
LEFT JOIN temporal_match AS tm ON d.delivery_id = tm.delivery_id
LEFT JOIN current_match AS cm ON d.supplier_id = cm.supplier_id
