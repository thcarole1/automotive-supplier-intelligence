SELECT
    part_id,
    part_code,
    part_name,
    family,
    subcategory,
    criticality,
    unit_of_measure
FROM {{ ref('stg_parts') }}
