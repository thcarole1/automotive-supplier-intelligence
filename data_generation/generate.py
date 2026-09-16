"""
Point d'entrée du générateur de données ASIP.
Orchestre la génération, l'injection d'anomalies et l'insertion en base,
dans l'ordre imposé par les dépendances de clés étrangères.
"""

import logging
import random
from faker import Faker

from data_generation.config import SEED
from data_generation.db import get_connection, insert_and_get_ids
from data_generation.anomalies import (
    inject_supplier_duplicates,
    inject_supplier_name_variants,
    inject_inconsistent_dates,
    inject_extreme_prices,
    inject_missing_values,
)
from data_generation.generators.suppliers import generate_suppliers
from data_generation.generators.parts import generate_parts
from data_generation.generators.purchase_orders import generate_purchase_orders
from data_generation.generators.deliveries import generate_deliveries
from data_generation.generators.quality_incidents import generate_quality_incidents
from data_generation.generators.inventory_snapshots import generate_inventory_snapshots

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


def main() -> None:
    Faker.seed(SEED)
    random.seed(SEED)
    fake = Faker()

    conn = get_connection()

    # --- suppliers ---
    suppliers = generate_suppliers(fake)
    suppliers = inject_supplier_duplicates(suppliers)
    suppliers = inject_supplier_name_variants(suppliers)
    supplier_ids = insert_and_get_ids(conn, "suppliers", suppliers, "supplier_id")
    supplier_risk_by_id = {
        sid: s["risk_profile"] for sid, s in zip(supplier_ids, suppliers)
    }
    logger.info("suppliers : %d lignes insérées", len(supplier_ids))

    # --- parts ---
    parts = generate_parts(fake)
    part_ids = insert_and_get_ids(conn, "parts", parts, "part_id")
    part_subcategory_by_id = {
        pid: p["subcategory"] for pid, p in zip(part_ids, parts)
    }
    logger.info("parts : %d lignes insérées", len(part_ids))

    # --- purchase_orders ---
    purchase_orders = generate_purchase_orders(fake, supplier_ids, part_subcategory_by_id)
    purchase_orders = inject_inconsistent_dates(
        purchase_orders, "confirmed_delivery_date", "order_date"
    )
    purchase_orders = inject_extreme_prices(purchase_orders)
    purchase_orders = inject_missing_values(purchase_orders, "confirmed_delivery_date")
    po_ids = insert_and_get_ids(conn, "purchase_orders", purchase_orders, "po_id")
    for po, po_id in zip(purchase_orders, po_ids):
        po["po_id"] = po_id
    po_part_id_by_po_id = {po["po_id"]: po["part_id"] for po in purchase_orders}
    logger.info("purchase_orders : %d lignes insérées", len(po_ids))

    # --- deliveries ---
    deliveries = generate_deliveries(fake, purchase_orders, supplier_risk_by_id)
    deliveries = inject_inconsistent_dates(
        deliveries, "actual_delivery_date", "shipment_date"
    )
    deliveries = inject_missing_values(deliveries, "shipment_date")
    delivery_ids = insert_and_get_ids(conn, "deliveries", deliveries, "delivery_id")
    logger.info("deliveries : %d lignes insérées", len(delivery_ids))

    deliveries_by_part_id: dict = {}
    for delivery in deliveries:
        part_id = po_part_id_by_po_id[delivery["po_id"]]
        deliveries_by_part_id.setdefault(part_id, []).append(delivery)

    # --- quality_incidents ---
    quality_incidents = generate_quality_incidents(
        fake, purchase_orders, supplier_risk_by_id, supplier_ids, part_ids
    )
    incident_ids = insert_and_get_ids(
        conn, "quality_incidents", quality_incidents, "incident_id"
    )
    logger.info("quality_incidents : %d lignes insérées", len(incident_ids))

    # --- inventory_snapshots ---
    inventory_snapshots = generate_inventory_snapshots(part_ids, deliveries_by_part_id)
    snapshot_ids = insert_and_get_ids(
        conn, "inventory_snapshots", inventory_snapshots, "snapshot_id"
    )
    logger.info("inventory_snapshots : %d lignes insérées", len(snapshot_ids))

    conn.close()
    logger.info("Génération terminée.")


if __name__ == "__main__":
    main()
