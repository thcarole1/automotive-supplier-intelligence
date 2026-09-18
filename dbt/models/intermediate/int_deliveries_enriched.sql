SELECT
    d.delivery_id,
    d.po_id,
    po.supplier_id,
    po.part_id,
    d.shipment_date,
    d.expected_delivery_date,
    d.actual_delivery_date,
    d.quantity_delivered,
    (d.actual_delivery_date - d.expected_delivery_date) AS delay_days,
    CASE
        WHEN d.actual_delivery_date IS NULL THEN NULL
        WHEN d.actual_delivery_date <= d.expected_delivery_date THEN TRUE
        ELSE FALSE
    END AS is_on_time
FROM {{ ref('stg_deliveries') }} AS d
LEFT JOIN {{ ref('stg_purchase_orders') }} AS po
    ON d.po_id = po.po_id
