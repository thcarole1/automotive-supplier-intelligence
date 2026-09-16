"""
Injection centralisée d'anomalies dans les données générées.
Chaque fonction retourne une nouvelle liste, sans muter l'originale.
Ces fonctions sont appelées explicitement par generate.py, sur les
champs pertinents de chaque table.
"""

import copy
import random
from data_generation.config import ANOMALY_RATE

SUPPLIER_NAME_VARIANT_SUFFIXES = ["", " SA", " Inc.", " GmbH"]


def inject_supplier_duplicates(suppliers: list[dict]) -> list[dict]:
    """
    Duplique certaines lignes de suppliers avec un nouveau supplier_code,
    simulant une même entreprise saisie deux fois dans l'ERP
    (le vrai doublon métier : même fournisseur, codes différents).
    """
    result = list(suppliers)
    num_duplicates = round(len(suppliers) * ANOMALY_RATE)
    next_index = len(suppliers) + 1
    for supplier in random.sample(suppliers, min(num_duplicates, len(suppliers))):
        duplicate = copy.deepcopy(supplier)
        duplicate["supplier_code"] = f"SUP-{next_index:04d}"
        next_index += 1
        result.append(duplicate)
    return result


def inject_supplier_name_variants(suppliers: list[dict]) -> list[dict]:
    """
    Sur un sous-ensemble de fournisseurs, fait varier la casse et/ou ajoute
    un suffixe au supplier_name, en gardant le même supplier_code
    (le code reste la clé métier propre ; le nom porte le bruit).
    """
    num_affected = round(len(suppliers) * ANOMALY_RATE)
    affected = random.sample(suppliers, min(num_affected, len(suppliers)))
    for supplier in affected:
        variant_style = random.choice(["upper", "suffix"])
        if variant_style == "upper":
            supplier["supplier_name"] = supplier["supplier_name"].upper()
        else:
            suffix = random.choice(SUPPLIER_NAME_VARIANT_SUFFIXES)
            supplier["supplier_name"] = f"{supplier['supplier_name']}{suffix}"
    return suppliers


def inject_inconsistent_dates(records: list[dict], before_field: str, after_field: str) -> list[dict]:
    """
    Échange before_field et after_field sur un sous-ensemble d'enregistrements
    (ex. confirmed_delivery_date / order_date), simulant une incohérence de
    saisie. Ne touche que les enregistrements où les deux champs existent.
    """
    eligible = [r for r in records if r.get(before_field) and r.get(after_field)]
    num_affected = round(len(eligible) * ANOMALY_RATE)
    affected = random.sample(eligible, min(num_affected, len(eligible)))
    for record in affected:
        record[before_field], record[after_field] = record[after_field], record[before_field]
    return records


def inject_extreme_prices(purchase_orders: list[dict]) -> list[dict]:
    """Remplace unit_price par une valeur aberrante (trop basse ou trop haute) sur un sous-ensemble."""
    num_affected = round(len(purchase_orders) * ANOMALY_RATE)
    affected = random.sample(purchase_orders, min(num_affected, len(purchase_orders)))
    for po in affected:
        po["unit_price"] = random.choice([0.01, round(random.uniform(10000, 50000), 2)])
    return purchase_orders


def inject_missing_values(records: list[dict], field: str) -> list[dict]:
    """Met field à None sur un sous-ensemble d'enregistrements."""
    eligible = [r for r in records if r.get(field) is not None]
    num_affected = round(len(eligible) * ANOMALY_RATE)
    affected = random.sample(eligible, min(num_affected, len(eligible)))
    for record in affected:
        record[field] = None
    return records
