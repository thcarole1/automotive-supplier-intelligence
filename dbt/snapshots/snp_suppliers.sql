{% snapshot snp_suppliers %}

{{
    config(
        target_schema='snapshots',
        unique_key='supplier_id',
        strategy='check',
        check_cols=['risk_profile', 'is_active'],
    )
}}

SELECT
    supplier_id,
    supplier_code,
    supplier_name,
    country,
    supplier_type,
    risk_profile,
    is_active
FROM {{ source('raw', 'suppliers') }}

{% endsnapshot %}
