SELECT
    delivery_id,
    po_id,
    shipment_date,
    expected_delivery_date,
    actual_delivery_date,
    quantity_delivered,
    created_at
FROM {{ source('raw', 'deliveries') }}
