-- ASIP : schéma PostgreSQL (raw)
-- Ordre de création respectant les dépendances de clés étrangères

CREATE TABLE suppliers (
    supplier_id     SERIAL PRIMARY KEY,
    supplier_code   VARCHAR(20) UNIQUE NOT NULL,
    supplier_name   VARCHAR(150) NOT NULL,
    country         VARCHAR(2) NOT NULL,
    supplier_type   VARCHAR(20) NOT NULL
                    CHECK (supplier_type IN ('TIER1', 'TIER2', 'RAW_MATERIAL')),
    risk_profile    VARCHAR(10) NOT NULL
                    CHECK (risk_profile IN ('LOW', 'MEDIUM', 'HIGH')),
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMP NOT NULL DEFAULT now()
);

CREATE TABLE parts (
    part_id         SERIAL PRIMARY KEY,
    part_code       VARCHAR(20) UNIQUE NOT NULL,
    part_name       VARCHAR(150) NOT NULL,
    family          VARCHAR(30) NOT NULL
                    CHECK (family IN ('SUSPENSION', 'ELECTRIC_POWERTRAIN')),
    subcategory     VARCHAR(30) NOT NULL,
    criticality     VARCHAR(10) NOT NULL
                    CHECK (criticality IN ('LOW', 'MEDIUM', 'HIGH')),
    unit_of_measure VARCHAR(10) NOT NULL,
    created_at      TIMESTAMP NOT NULL DEFAULT now()
);

CREATE TABLE purchase_orders (
    po_id                     SERIAL PRIMARY KEY,
    po_number                 VARCHAR(20) UNIQUE NOT NULL,
    supplier_id               INTEGER NOT NULL REFERENCES suppliers(supplier_id),
    part_id                   INTEGER NOT NULL REFERENCES parts(part_id),
    order_date                DATE NOT NULL,
    requested_delivery_date   DATE NOT NULL,
    confirmed_delivery_date   DATE,
    quantity                  INTEGER NOT NULL,
    unit_price                NUMERIC(10, 2) NOT NULL,
    currency                  VARCHAR(3) NOT NULL DEFAULT 'EUR',
    created_at                TIMESTAMP NOT NULL DEFAULT now()
);

CREATE TABLE deliveries (
    delivery_id             SERIAL PRIMARY KEY,
    po_id                   INTEGER NOT NULL REFERENCES purchase_orders(po_id),
    shipment_date           DATE,
    expected_delivery_date  DATE NOT NULL,
    actual_delivery_date    DATE,
    quantity_delivered      INTEGER NOT NULL,
    created_at               TIMESTAMP NOT NULL DEFAULT now()
);

CREATE TABLE quality_incidents (
    incident_id         SERIAL PRIMARY KEY,
    supplier_id         INTEGER NOT NULL REFERENCES suppliers(supplier_id),
    part_id              INTEGER NOT NULL REFERENCES parts(part_id),
    po_id                INTEGER REFERENCES purchase_orders(po_id),
    incident_date        DATE NOT NULL,
    incident_type        VARCHAR(30) NOT NULL,
    severity             VARCHAR(10) NOT NULL
                         CHECK (severity IN ('MINOR', 'MAJOR', 'CRITICAL')),
    quantity_affected    INTEGER NOT NULL,
    created_at            TIMESTAMP NOT NULL DEFAULT now()
);

CREATE TABLE inventory_snapshots (
    snapshot_id      SERIAL PRIMARY KEY,
    part_id           INTEGER NOT NULL REFERENCES parts(part_id),
    snapshot_date     DATE NOT NULL,
    stock_quantity    INTEGER NOT NULL,
    safety_stock      INTEGER NOT NULL,
    created_at         TIMESTAMP NOT NULL DEFAULT now(),
    UNIQUE (part_id, snapshot_date)
);
