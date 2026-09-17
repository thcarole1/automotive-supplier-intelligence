SELECT
    snapshot_id,
    part_id,
    snapshot_date,
    stock_quantity,
    safety_stock,
    created_at
FROM {{ source('raw', 'inventory_snapshots') }}
