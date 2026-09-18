SELECT
    snapshot_id,
    part_id,
    snapshot_date,
    stock_quantity,
    safety_stock,
    (stock_quantity < safety_stock) AS is_below_safety_stock
FROM {{ ref('stg_inventory_snapshots') }}
