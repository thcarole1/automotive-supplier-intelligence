SELECT
    dbt_scd_id AS supplier_key,
    supplier_id,
    supplier_code,
    supplier_name,
    country,
    supplier_type,
    risk_profile,
    is_active,
    dbt_valid_from AS valid_from,
    dbt_valid_to AS valid_to,
    (dbt_valid_to IS NULL) AS is_current
FROM {{ ref('snp_suppliers') }}
