SELECT
    supplier_id,
    supplier_code,
    TRIM(supplier_name) AS supplier_name,
    country,
    supplier_type,
    risk_profile,
    is_active,
    created_at
FROM {{ source('raw', 'suppliers') }}
