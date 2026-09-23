# ADR-0002: Deliberately minimal 6-table scope

## Context

Modeling a real ERP/procurement system potentially covers many entities: suppliers, parts, orders, deliveries, quality, stock, but also contracts, exchange rates, production plans, invoices, etc. This project aims to demonstrate relational/transactional modeling skills (star schema, SCD2, multi-fact), without being a full ERP. The exact functional scope to cover in v1 needs to be decided.

## Decision

The v1 scope is deliberately limited to 6 tables: `suppliers`, `parts`, `purchase_orders`, `deliveries`, `quality_incidents`, `inventory_snapshots`. The `contracts`, `fx_rate`, and `production_plan` entities are explicitly excluded from v1. An extension remains possible if time allows.

## Why

- These 6 tables are enough to cover the full causal chain the project targets (supplier risk leading to delivery delay leading to stockout, supplier risk leading to a quality incident), which is the central narrative to demonstrate.
- They allow building a realistic star schema with 4 dimensions and 4 facts, including an SCD2 case on `dim_supplier`, without unnecessary complexity.
- Alternative considered: adding `fx_rate` to handle multiple currencies. Dismissed because it would complicate KPI calculations without demonstrating additional modeling skill (it's a data conversion topic, not relational modeling).
- Alternative considered: adding `contracts` to link negotiated prices and terms to orders. Dismissed for v1 because it adds another temporal dimension (a contract's validity period) that could have diluted the focus on `dim_supplier`'s SCD2.
- A broader scope would risk diluting the project's signal (relational modeling) rather than strengthening it, following the same logic as excluding Spark, Kafka, and Terraform (see ADR-0001).

## Consequences

- Financial KPIs stay in their original currency, with no conversion (a limitation already documented while designing `purchase_orders`).
- No negotiated contract pricing is handled at this stage: `unit_price` on `purchase_orders` is a raw value, not derived from a contract.
- Extending toward `contracts`, `fx_rate`, or `production_plan` will require a dedicated ADR if decided later on.
- The README must reflect this deliberately minimal scope, to avoid any impression of an oversight in interviews.
