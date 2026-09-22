SELECT
    supplier_id,
    supplier_code,
    supplier_name,
    country,
    supplier_type,
    risk_profile,
    is_active
FROM {{ ref('dim_supplier') }}
WHERE is_current
