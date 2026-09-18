SELECT
    po.po_id,
    po.po_number,
    po.supplier_id,
    s.risk_profile AS supplier_risk_profile,
    s.country AS supplier_country,
    po.part_id,
    p.family AS part_family,
    p.subcategory AS part_subcategory,
    p.criticality AS part_criticality,
    po.order_date,
    po.requested_delivery_date,
    po.confirmed_delivery_date,
    po.quantity,
    po.unit_price,
    (po.quantity * po.unit_price) AS line_total,
    po.currency
FROM {{ ref('stg_purchase_orders') }} AS po
LEFT JOIN {{ ref('stg_suppliers') }} AS s
    ON po.supplier_id = s.supplier_id
LEFT JOIN {{ ref('stg_parts') }} AS p
    ON po.part_id = p.part_id
