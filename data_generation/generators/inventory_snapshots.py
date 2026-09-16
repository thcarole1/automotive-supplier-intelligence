"""
Génère les données de la table inventory_snapshots.

Simule une trajectoire de stock jour par jour pour chaque pièce :
le stock diminue selon une consommation quotidienne stable (proxy
de cadence de production, hors périmètre v1, usines actives 7j/7) et
augmente aux dates de livraison réelles issues de deliveries.py.
Le stock est plafonné à 0 en cas de rupture (pas de valeur négative).
"""

import random
from datetime import timedelta
from data_generation.config import (
    START_DATE,
    END_DATE,
    DAILY_CONSUMPTION_RANGE,
    SAFETY_STOCK_DAYS_COVERAGE,
    INITIAL_STOCK_DAYS_COVERAGE,
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
        daily_consumption = random.randint(*DAILY_CONSUMPTION_RANGE)
        safety_stock = daily_consumption * SAFETY_STOCK_DAYS_COVERAGE
        stock = daily_consumption * INITIAL_STOCK_DAYS_COVERAGE

        # Index des réapprovisionnements réels par date, pour cette pièce
        deliveries_by_date: dict = {}
        for delivery in deliveries_by_part_id.get(part_id, []):
            actual_date = delivery["actual_delivery_date"]
            if actual_date is not None:
                deliveries_by_date.setdefault(actual_date, 0)
                deliveries_by_date[actual_date] += delivery["quantity_delivered"]

        current_date = START_DATE
        for _ in range(num_days):
            stock += deliveries_by_date.get(current_date, 0)
            stock -= daily_consumption
            stock = max(stock, 0)

            snapshots.append({
                "part_id": part_id,
                "snapshot_date": current_date,
                "stock_quantity": stock,
                "safety_stock": safety_stock,
            })

            current_date += timedelta(days=1)

    return snapshots
