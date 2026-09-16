"""
Génère les données de la table deliveries.
"""

import random
from datetime import timedelta
from faker import Faker
from data_generation.config import (
    END_DATE,
    DELIVERY_DELAY_RANGES_BY_RISK,
    MAJOR_DELAY_EXTRA_DAYS,
    PARTIAL_DELIVERY_RATE,
    IN_PROGRESS_WINDOW_DAYS,
    IN_PROGRESS_PROBABILITY,
)


def _draw_delay_days(risk_profile: str) -> int:
    """Tire un écart (en jours) entre date confirmée et date réelle, selon le risque fournisseur."""
    params = DELIVERY_DELAY_RANGES_BY_RISK[risk_profile]
    jitter_min, jitter_max = params["jitter_days"]
    delay = random.randint(jitter_min, jitter_max)
    if random.random() < params["major_delay_prob"]:
        extra_min, extra_max = MAJOR_DELAY_EXTRA_DAYS
        delay += random.randint(extra_min, extra_max)
    return delay


def _is_in_progress(confirmed_delivery_date) -> bool:
    """Détermine si une commande récente est encore en cours (pas encore livrée)."""
    days_before_end = (END_DATE - confirmed_delivery_date).days
    if 0 <= days_before_end <= IN_PROGRESS_WINDOW_DAYS:
        return random.random() < IN_PROGRESS_PROBABILITY
    return False


def generate_deliveries(
    fake: Faker,
    purchase_orders: list[dict],
    supplier_risk_by_id: dict[int, str],
) -> list[dict]:
    """
    Génère une ou plusieurs livraisons par commande.
    Le retard dépend du profil de risque du fournisseur.
    Certaines commandes récentes sont simulées comme "en cours" (non livrées).
    Les livraisons complètes correspondent exactement à la quantité commandée ;
    les écarts de quantité sont réservés au module anomalies.py.
    """
    deliveries = []

    for po in purchase_orders:
        risk_profile = supplier_risk_by_id[po["supplier_id"]]
        confirmed = po["confirmed_delivery_date"] or po["requested_delivery_date"]
        in_progress = _is_in_progress(confirmed)

        is_partial = random.random() < PARTIAL_DELIVERY_RATE
        num_shipments = 2 if is_partial else 1
        remaining_qty = po["quantity"]

        for shipment_index in range(num_shipments):
            qty_this_shipment = (
                remaining_qty // (num_shipments - shipment_index)
            )
            remaining_qty -= qty_this_shipment

            shipment_date = confirmed - timedelta(days=random.randint(2, 6))

            if in_progress and shipment_index == num_shipments - 1:
                actual_delivery_date = None
                shipment_date = None if random.random() < 0.3 else shipment_date
            else:
                delay = _draw_delay_days(risk_profile)
                actual_delivery_date = confirmed + timedelta(days=delay)

            delivery = {
                "po_id": po["po_id"],
                "shipment_date": shipment_date,
                "expected_delivery_date": confirmed,
                "actual_delivery_date": actual_delivery_date,
                "quantity_delivered": qty_this_shipment,
            }
            deliveries.append(delivery)

    return deliveries
