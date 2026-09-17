SELECT
    incident_id,
    supplier_id,
    part_id,
    po_id,
    incident_date,
    incident_type,
    severity,
    quantity_affected,
    created_at
FROM {{ source('raw', 'quality_incidents') }}
