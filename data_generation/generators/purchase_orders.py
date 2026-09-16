"""
Génère les données de la table purchase_orders.
"""

import random
from datetime import timedelta
from faker import Faker
from data_generation.config import (
    NUM_PURCHASE_ORDERS,
    START_DATE,
    END_DATE,
    PART_PRICE_RANGES,
)


def generate_purchase_orders(
    fake: Faker,
    supplier_ids: list[int],
    part_subcategory_by_id: dict[int, str],
) -> list[dict]:
    """
    Génère une liste de dictionnaires représentant des commandes.
    Le prix unitaire est tiré selon une fourchette réaliste propre
    à la sous-catégorie de la pièce commandée.
    La devise reste fixée à EUR en v1 (voir ADR sur le périmètre hors fx_rate).
    """
    part_ids = list(part_subcategory_by_id.keys())
    purchase_orders = []

    for i in range(1, NUM_PURCHASE_ORDERS + 1):
        order_date = fake.date_between(start_date=START_DATE, end_date=END_DATE)
        lead_time_days = random.randint(7, 45)
        requested_delivery_date = order_date + timedelta(days=lead_time_days)

        confirmation_shift = random.randint(-3, 10)
        confirmed_delivery_date = requested_delivery_date + timedelta(days=confirmation_shift)

        part_id = fake.random_element(part_ids)
        subcategory = part_subcategory_by_id[part_id]
        price_min, price_max = PART_PRICE_RANGES[subcategory]

        po = {
            "po_number": f"PO-{i:05d}",
            "supplier_id": fake.random_element(supplier_ids),
            "part_id": part_id,
            "order_date": order_date,
            "requested_delivery_date": requested_delivery_date,
            "confirmed_delivery_date": confirmed_delivery_date,
            "quantity": random.randint(10, 500),
            "unit_price": round(random.uniform(price_min, price_max), 2),
            "currency": "EUR",
        }
        purchase_orders.append(po)
    return purchase_orders
