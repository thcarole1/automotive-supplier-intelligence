# ADR-0001: Choosing local PostgreSQL over a cloud setup from the start

## Context

The two previous portfolio projects (*Electric Mobility Platform*, *EV Powertrain Manufacturing Analytics*) already demonstrate AWS cloud proficiency (S3, Glue/Athena, Lambda, MWAA, MSK, EMR Serverless) and infrastructure as code (Terraform). This third project aims to fill a different gap in the portfolio: relational/transactional data modeling (star schema, SCD2, multi-fact ERP/procurement style), absent from the two previous projects. The storage/processing infrastructure for this project needs to be decided.

## Decision

The v1 core of the project relies entirely on local services: PostgreSQL in a Docker container for storage, dbt for transformation, Airflow locally (Docker) for orchestration, Power BI with a direct connection for reporting. No managed cloud service is used at this stage. An AWS track is explicitly out of scope for v1, to be reevaluated in a dedicated session once the local core is complete.

## Why

- AWS cloud is already demonstrated in depth elsewhere in the portfolio; repeating it here would dilute the signal rather than strengthen it.
- This project's differentiating goal is relational modeling (star schema, SCD2), a topic orthogonal to the cloud vs. local infrastructure choice. Staying local allows focusing on it without added cost or complexity.
- Alternative considered: Snowflake or managed Postgres (RDS) from the start, dismissed because it would introduce cloud cost and configuration dependencies without adding differentiating value for this v1.
- Alternative considered: SQLite for further simplicity, dismissed because PostgreSQL is the de facto standard in a real ERP/procurement environment and natively supports the constraints and types needed for the model (SCD2, foreign keys, window functions).

## Consequences

- The project is reproducible locally via `docker compose up`, with no dependency on a cloud account or associated cost.
- A future cloud migration (if validated in a dedicated session) will require its own ADR and is not anticipated in the current modeling choices.
- The README must explicitly state this choice to avoid any ambiguity in interviews about the absence of cloud in this particular project.
