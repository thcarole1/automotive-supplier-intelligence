SELECT
    po_id,
    po_number,
    supplier_id,
    part_id,
    order_date,
    requested_delivery_date,
    confirmed_delivery_date,
    quantity,
    unit_price,
    currency,
    created_at
FROM {{ source('raw', 'purchase_orders') }}
