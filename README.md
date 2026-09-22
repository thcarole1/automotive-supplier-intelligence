# Automotive Supplier Intelligence Platform (ASIP)

> ⚠️ Projet en cours de construction. Ce README sera mis à jour à chaque clôture de phase.

## En bref

Plateforme d'intelligence fournisseurs pour une entreprise automobile fictive (**ElectroMotion Automotive**). Ce projet est le 3ᵉ d'un portfolio de reconversion Data Engineering et couvre un trou volontairement laissé par les deux précédents : la **modélisation de données relationnelle/transactionnelle métier** (star schema, SCD2, multi-facts de type ERP/achats), sur un domaine directement lié à une expérience achats/fournisseurs.

Les données et le nom de l'entreprise sont **entièrement fictifs**, sans lien avec des données confidentielles d'un employeur réel.

## Schéma d'architecture

```mermaid
flowchart LR
    A[Générateur Python<br/>Faker, seed fixe] --> B[(PostgreSQL<br/>raw)]
    B --> C[dbt<br/>staging → intermediate → marts]
    C --> D[Power BI<br/>connexion directe]
    E[Airflow<br/>Docker] -. orchestre .-> A
    E -. orchestre .-> C
```

## Données générées

Le générateur Python (Faker, seed fixe) produit un jeu de données reproductible sur la période 2023-01-01 à 2025-12-31 :

| Table | Volume |
|---|---|
| `suppliers` | 26 (dont doublons volontaires) |
| `parts` | 40 |
| `purchase_orders` | 2 000 |
| `deliveries` | 2 307 (dont livraisons partielles) |
| `quality_incidents` | 162 |
| `inventory_snapshots` | 43 840 |

Anomalies injectées volontairement (~4 % du volume) : doublons fournisseurs, variantes orthographiques de noms, dates incohérentes, prix aberrants, valeurs manquantes. Détectées par les tests dbt (voir le graphe de lignage ci-dessous).

## Modèle de données (star schema)

3 dimensions (dont `dim_supplier` avec historisation SCD2) et 4 tables de faits, obtenues via un pipeline dbt en 3 couches (staging → intermediate → marts).

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#e3f2fd', 'primaryTextColor': '#0d1b2a', 'primaryBorderColor': '#1565c0', 'lineColor': '#333333', 'tertiaryColor': '#fff3e0'}}}%%
erDiagram
    dim_supplier ||--o{ fct_purchase_order_line : "supplier_key"
    dim_supplier ||--o{ fct_delivery : "supplier_key"
    dim_supplier ||--o{ fct_quality_incident : "supplier_key"
    dim_part ||--o{ fct_purchase_order_line : "part_id"
    dim_part ||--o{ fct_quality_incident : "part_id"
    dim_part ||--o{ fct_inventory_snapshot : "part_id"
    fct_purchase_order_line ||--o{ fct_delivery : "po_id"
    dim_date ||--o{ fct_purchase_order_line : "order_date"
    dim_date ||--o{ fct_inventory_snapshot : "snapshot_date"

    dim_supplier {
        string supplier_key PK
        int supplier_id
        string risk_profile
        boolean is_current
    }
    dim_part {
        int part_id PK
        string family
        string criticality
    }
    dim_date {
        date date_day PK
    }
    fct_purchase_order_line {
        int po_id PK
        string supplier_key FK
        int part_id FK
        numeric line_total
    }
    fct_delivery {
        int delivery_id PK
        int po_id FK
        string supplier_key FK
        int delay_days
    }
    fct_quality_incident {
        int incident_id PK
        string supplier_key FK
        int part_id FK
        string severity
    }
    fct_inventory_snapshot {
        int snapshot_id PK
        int part_id FK
        boolean is_below_safety_stock
    }
```

`supplier_key` (et non `supplier_id`) est utilisé comme clé étrangère dans les faits : c'est la clé de version SCD2, qui pointe vers la version du fournisseur active à la date du fait (voir [ADR-0004](docs/adr/0004-fallback-scd2-facts.md)).

### Documentation dbt et graphe de lignage

dbt génère une documentation interactive avec un graphe de lignage complet (raw → staging → intermediate → marts), consultable en local :

```bash
cd dbt
dbt docs generate
dbt docs serve
```

Le graphe de lignage réel du projet (généré à partir des 15 modèles et de leurs dépendances) :

![Graphe de lignage dbt](docs/img/dbt-lineage-graph.png)

## KPI calculés

5 indicateurs métier, calculés par des modèles dbt dédiés (`models/marts/kpi_*.sql`) : OTD, PPM qualité, lead time moyen et variabilité (par fournisseur), Days of Supply (par pièce), et un Supplier Health Score composite.

### Supplier Health Score, en deux étapes

Le score combine deux niveaux de pondération, tous deux configurables sans toucher au SQL (`dbt_project.yml`, variables `health_score_criticality_weights` et `health_score_kpi_weights`) :

1. **L'OTD est d'abord pondéré par criticité des pièces** : un retard sur une pièce critique (HIGH) pèse plus lourd qu'un retard sur une pièce secondaire (LOW).
2. **Ce résultat est ensuite combiné avec le PPM et la variabilité du lead time** (tous deux classés par rang relatif entre fournisseurs, pour rester comparables), afin d'obtenir le score final sur 100.

```mermaid
flowchart TD
    A1[OTD pièces LOW] --> C1
    A2[OTD pièces MEDIUM] --> C1
    A3[OTD pièces HIGH] --> C1
    C1([otd_weighted_by_criticality<br/>pondéré 20% / 30% / 50%])

    C1 --> D
    B1[PPM classé entre fournisseurs] --> D
    B2[Variabilité du lead time classée] --> D
    D([health_score sur 100<br/>pondéré 40% / 40% / 20%])

    classDef inputStyle fill:#f5f5f5,stroke:#9e9e9e,stroke-width:1px,color:#212121
    classDef resultStyle fill:#eef2f7,stroke:#5c7a99,stroke-width:1px,color:#212121
    class A1,A2,A3,B1,B2 inputStyle
    class C1,D resultStyle
```

## Orchestration Airflow

Un DAG unique (`asip_pipeline`) orchestre le pipeline de bout en bout : génération/ingestion des données, `dbt run`, `dbt test`, puis publication d'un résumé des KPI dans les logs. Airflow tourne en local via Docker (image versionnée, LocalExecutor, base de métadonnées dédiée).

Exécution réelle du DAG, les 4 tâches en succès :

![Graphe du DAG Airflow](docs/img/airflow-dag-graph.png)

## Stack


- **Génération de données** : Python, Faker (seed fixe, reproductible)
- **Stockage** : PostgreSQL (Docker)
- **Transformation** : dbt (star schema, SCD2 sur `dim_supplier`)
- **Orchestration** : Airflow (Docker, image versionnée)
- **Restitution** : Power BI

*(Volet cloud AWS explicitement hors périmètre v1, voir [ADR-0001](docs/adr/0001-postgres-local-vs-cloud-demblee.md))*

## Démarrage

```bash
git clone <repo>
cd automotive-supplier-intelligence
docker compose up
```

## État du projet

- Phases terminées : 0/4
- Tests dbt : 0
- ADR rédigés : 4

## Pistes d'extension (hors périmètre v1)

- **Consommation multi-usines par pays** : le modèle de stock actuel simule une consommation quotidienne globale par pièce, sans distinction géographique. Une évolution réaliste consisterait à répartir la consommation entre plusieurs usines localisées dans différents pays, avec des cadences propres à chaque site. Nécessiterait l'introduction d'une entité plant/usine, aujourd'hui absente des données sources.
- **dim_plant** : initialement prévue dans le cahier des charges, cette dimension a été retirée du périmètre v1, faute de table source portant une notion d'usine (voir [ADR-0003](docs/adr/0003-retrait-dim-plant.md)). Elle pourrait revenir si la piste multi-usines ci-dessus est concrétisée.
- **Historique SCD2 sur les facts** : le SCD2 de dim_supplier n'a été activé qu'après la génération initiale des données (2023-2025), donc les facts historiques référencent tous la version actuelle du fournisseur plutôt que celle en vigueur à leur date réelle (voir [ADR-0004](docs/adr/0004-fallback-scd2-facts.md)). Un nouveau fait généré après un changement de risk_profile bénéficiera d'une correspondance temporelle exacte.

## Documentation approfondie

- [ADR-0001 : Choix de PostgreSQL local plutôt qu'un socle cloud d'emblée](docs/adr/0001-postgres-local-vs-cloud-demblee.md)
- [ADR-0002 : Périmètre volontairement minimal de 6 tables](docs/adr/0002-perimetre-six-tables.md)
- [ADR-0003 : Retrait de dim_plant du périmètre v1](docs/adr/0003-retrait-dim-plant.md)
- [ADR-0004 : Fallback vers la version courante pour la jointure temporelle SCD2](docs/adr/0004-fallback-scd2-facts.md)
