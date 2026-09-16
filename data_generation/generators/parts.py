"""
Génère les données de la table parts.
"""

from collections import OrderedDict
from faker import Faker
from data_generation.config import NUM_PARTS, PART_FAMILIES

CRITICALITY_WEIGHTS_BY_FAMILY = {
    "SUSPENSION": OrderedDict([
        ("LOW", 0.40),
        ("MEDIUM", 0.40),
        ("HIGH", 0.20),
    ]),
    "ELECTRIC_POWERTRAIN": OrderedDict([
        ("LOW", 0.15),
        ("MEDIUM", 0.35),
        ("HIGH", 0.50),
    ]),
}


def generate_parts(fake: Faker) -> list[dict]:
    """
    Génère une liste de dictionnaires représentant des pièces,
    réparties entre les deux familles définies dans PART_FAMILIES.
    La criticité est pondérée différemment selon la famille :
    l'électronique de puissance est plus souvent critique que la suspension.
    """
    families = list(PART_FAMILIES.keys())
    parts = []
    for i in range(1, NUM_PARTS + 1):
        family = fake.random_element(families)
        subcategory = fake.random_element(PART_FAMILIES[family])
        criticality_weights = CRITICALITY_WEIGHTS_BY_FAMILY[family]
        part = {
            "part_code": f"PRT-{i:04d}",
            "part_name": f"{subcategory.replace('_', ' ').capitalize()} {fake.bothify('##-???')}",
            "family": family,
            "subcategory": subcategory,
            "criticality": fake.random_element(elements=criticality_weights),
            "unit_of_measure": "EA",
        }
        parts.append(part)
    return parts
