"""
Génère les données de la table suppliers.
"""

from collections import OrderedDict
from faker import Faker
from data_generation.config import (
    NUM_SUPPLIERS,
    SUPPLIER_TYPES,
    SUPPLIER_COUNTRIES,
)

RISK_PROFILE_WEIGHTS = OrderedDict([
    ("LOW", 0.50),
    ("MEDIUM", 0.35),
    ("HIGH", 0.15),
])


def generate_suppliers(fake: Faker) -> list[dict]:
    """
    Génère une liste de dictionnaires représentant des fournisseurs.
    Les anomalies (doublons, variantes de nom) sont injectées séparément
    par le module anomalies.py, pas ici.
    """
    suppliers = []
    for i in range(1, NUM_SUPPLIERS + 1):
        supplier = {
            "supplier_code": f"SUP-{i:04d}",
            "supplier_name": fake.company(),
            "country": fake.random_element(SUPPLIER_COUNTRIES),
            "supplier_type": fake.random_element(SUPPLIER_TYPES),
            "risk_profile": fake.random_element(elements=RISK_PROFILE_WEIGHTS),
            "is_active": fake.boolean(chance_of_getting_true=90),
        }
        suppliers.append(supplier)
    return suppliers
