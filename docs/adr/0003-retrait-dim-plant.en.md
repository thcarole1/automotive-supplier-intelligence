# ADR-0003: Removing dim_plant from the v1 scope

## Context

The initial requirements planned a `dim_plant` dimension among the dbt marts (`dim_supplier`, `dim_part`, `dim_plant`, `dim_date`). However, none of the 6 source tables in the v1 scope (`suppliers`, `parts`, `purchase_orders`, `deliveries`, `quality_incidents`, `inventory_snapshots`) contains any information about plants or production sites. A decision is needed on how to handle this inconsistency between the initial requirements and the data actually available.

## Decision

`dim_plant` is removed from the v1 scope. The marts are limited to `dim_supplier`, `dim_part`, and `dim_date`. A future extension toward a plant concept (multi-site, consumption by country) remains possible, and is already documented as an extension idea in the README.

## Why

- No source table carries this information: creating `dim_plant` now would require either an empty or fictional dimension with no real link to the facts, or adding a 7th source table.
- The 6-table scope has already been explicitly decided and documented as deliberately minimal (see ADR-0002). Adding another table now would revisit that decision without a sufficient new reason.
- Alternative considered: adding a `plants` table linked to `purchase_orders` or `inventory_snapshots`. Dismissed for v1 because it would complicate the model without real value for the project's narrative (relational modeling for procurement/quality/stock, not multi-site management).

## Consequences

- The final star schema has 3 dimensions (`dim_supplier`, `dim_part`, `dim_date`) instead of the 4 initially planned.
- The README must be updated to reflect this final mart scope, consistent with the extension idea already noted.
- If a v2 introduces a plant concept, it will require a new ADR and a new source table, not just adding a dimension.
