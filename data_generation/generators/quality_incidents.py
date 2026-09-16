"""
Génère les données de la table quality_incidents.
"""

import random
from faker import Faker
from data_generation.config import (
    START_DATE,
    END_DATE,
    INCIDENT_TYPES,
    INCIDENT_PROBABILITY_BY_RISK,
    ORPHAN_INCIDENT_RATE,
    SEVERITY_WEIGHTS,
    QUANTITY_AFFECTED_RATIO_RANGE,
)


def generate_quality_incidents(
    fake: Faker,
    purchase_orders: list[dict],
    supplier_risk_by_id: dict[int, str],
    supplier_ids: list[int],
    part_ids: list[int],
) -> list[dict]:
    """
    Génère des incidents qualité.
    La majorité découle d'une commande (po_id renseigné), avec une probabilité
    dépendant du profil de risque du fournisseur. Une minorité est "orpheline"
    (pas de po_id), simulant des audits qualité génériques.
    """
    incidents = []

    # Incidents rattachés à une commande
    for po in purchase_orders:
        risk_profile = supplier_risk_by_id[po["supplier_id"]]
        probability = INCIDENT_PROBABILITY_BY_RISK[risk_profile]

        if random.random() < probability:
            ratio_min, ratio_max = QUANTITY_AFFECTED_RATIO_RANGE
            ratio = random.uniform(ratio_min, ratio_max)
            quantity_affected = max(1, round(po["quantity"] * ratio))

            incident = {
                "supplier_id": po["supplier_id"],
                "part_id": po["part_id"],
                "po_id": po["po_id"],
                "incident_date": fake.date_between(
                    start_date=po["order_date"], end_date=END_DATE
                ),
                "incident_type": fake.random_element(INCIDENT_TYPES),
                "severity": fake.random_element(elements=SEVERITY_WEIGHTS),
                "quantity_affected": quantity_affected,
            }
            incidents.append(incident)

    # Incidents orphelins (sans po_id), volume proportionnel aux incidents déjà générés
    num_orphans = round(len(incidents) * ORPHAN_INCIDENT_RATE)
    for _ in range(num_orphans):
        supplier_id = fake.random_element(supplier_ids)
        risk_profile = supplier_risk_by_id[supplier_id]

        incident = {
            "supplier_id": supplier_id,
            "part_id": fake.random_element(part_ids),
            "po_id": None,
            "incident_date": fake.date_between(start_date=START_DATE, end_date=END_DATE),
            "incident_type": fake.random_element(INCIDENT_TYPES),
            "severity": fake.random_element(elements=SEVERITY_WEIGHTS),
            "quantity_affected": random.randint(1, 20),
        }
        incidents.append(incident)

    return incidents
