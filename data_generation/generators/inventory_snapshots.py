"""
Génère les données de la table inventory_snapshots.

Simule une trajectoire de stock jour par jour pour chaque pièce :
le stock diminue selon une consommation quotidienne dérivée du volume
réellement livré à cette pièce sur la période (pour rester cohérent avec
les quantités commandées), avec une variabilité aléatoire journalière.
Le stock augmente aux dates de livraison réelles issues de deliveries.py.

Un stock théorique est suivi en interne et peut devenir négatif,
représentant une rupture/backorder (demande non satisfaite qui s'accumule
jusqu'au prochain réapprovisionnement, pratique standard de simulation
d'inventaire). Seule la valeur physique (plafonnée à 0) est enregistrée
dans stock_quantity, pour éviter toute dérive artificielle du stock sur
la durée de la simulation.
"""

import random
from datetime import timedelta
from data_generation.config import (
    START_DATE,
    END_DATE,
    SAFETY_STOCK_DAYS_COVERAGE,
    INITIAL_STOCK_DAYS_COVERAGE,
    DAILY_CONSUMPTION_JITTER_RANGE,
)


def generate_inventory_snapshots(
    part_ids: list[int],
    deliveries_by_part_id: dict[int, list[dict]],
) -> list[dict]:
    """
    Génère un relevé de stock quotidien par pièce sur toute la période.
    """
    snapshots = []
    num_days = (END_DATE - START_DATE).days + 1

    for part_id in part_ids:
        deliveries = deliveries_by_part_id.get(part_id, [])
        total_delivered = sum(d["quantity_delivered"] for d in deliveries)
        avg_daily_consumption = max(total_delivered / num_days, 1.0)

        safety_stock = round(avg_daily_consumption * SAFETY_STOCK_DAYS_COVERAGE)
        theoretical_stock = round(avg_daily_consumption * INITIAL_STOCK_DAYS_COVERAGE)

        deliveries_by_date: dict = {}
        for delivery in deliveries:
            actual_date = delivery["actual_delivery_date"]
            if actual_date is not None:
                deliveries_by_date.setdefault(actual_date, 0)
                deliveries_by_date[actual_date] += delivery["quantity_delivered"]

        current_date = START_DATE
        for _ in range(num_days):
            jitter_min, jitter_max = DAILY_CONSUMPTION_JITTER_RANGE
            daily_consumption = round(avg_daily_consumption * random.uniform(jitter_min, jitter_max))

            theoretical_stock += deliveries_by_date.get(current_date, 0)
            theoretical_stock -= daily_consumption

            snapshots.append({
                "part_id": part_id,
                "snapshot_date": current_date,
                "stock_quantity": max(theoretical_stock, 0),
                "safety_stock": safety_stock,
            })

            current_date += timedelta(days=1)

    return snapshots
