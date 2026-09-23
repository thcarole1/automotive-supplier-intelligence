# ADR-0004: Falling back to the current version for the SCD2 temporal join

## Context

The fact tables reference `dim_supplier` via `supplier_key` (SCD2 version key), to associate each fact with the supplier version active at its date. The dbt snapshot (`snp_suppliers`) was first run in September 2026, so `dbt_valid_from` for the initial version corresponds to that date, well after the business dates of historical orders (2023-2025). A strict temporal join (fact date between `valid_from` and `valid_to`) therefore finds no match for any of the facts already present.

## Decision

When no SCD2 version is valid at the fact's date, the fact is associated with the supplier's current version (`is_current = TRUE`), rather than being left unmatched or causing a failure.

## Why

- SCD2 only captures history from the moment it is activated; it cannot retroactively reconstruct a history that was never recorded. This isn't a flaw in the model, but a normal consequence of starting SCD2 after the initial data generation.
- Alternative considered: dropping the temporal join and referencing `supplier_id` directly in the facts. Dismissed because it would strip SCD2 of its pedagogical value in the facts, even though this is a key point of the requirements.
- The fallback stays consistent with a real production system: any new fact generated after SCD2 is activated will benefit from a correct and meaningful temporal join.

## Consequences

- Historical facts (generated before SCD2 was activated) all reflect the supplier's current version, not the one in effect at their actual date. This is a known limitation, to be mentioned in the README.
- A new fact generated after an SCD2 change (e.g., a new order placed after a risk downgrade) will benefit from an exact temporal match, correctly demonstrating the mechanism.
