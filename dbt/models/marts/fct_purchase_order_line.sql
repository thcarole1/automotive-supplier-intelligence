WITH temporal_match AS (
    SELECT
        po.po_id,
        ds.supplier_key
    FROM {{ ref('int_purchase_orders_enriched') }} AS po
    LEFT JOIN {{ ref('dim_supplier') }} AS ds
        ON po.supplier_id = ds.supplier_id
        AND po.order_date >= CAST(ds.valid_from AS DATE)
        AND (ds.valid_to IS NULL OR po.order_date < CAST(ds.valid_to AS DATE))
),

current_match AS (
    SELECT supplier_id, supplier_key
    FROM {{ ref('dim_supplier') }}
    WHERE is_current
)

SELECT
    po.po_id,
    po.po_number,
    COALESCE(tm.supplier_key, cm.supplier_key) AS supplier_key,
    po.part_id,
    po.order_date,
    po.requested_delivery_date,
    po.confirmed_delivery_date,
    po.quantity,
    po.unit_price,
    po.line_total,
    po.currency
FROM {{ ref('int_purchase_orders_enriched') }} AS po
LEFT JOIN temporal_match AS tm ON po.po_id = tm.po_id
LEFT JOIN current_match AS cm ON po.supplier_id = cm.supplier_id
