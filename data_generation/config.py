"""
Configuration centrale du générateur de données ASIP.
Toute modification de volume ou de période se fait ici uniquement.
"""

from collections import OrderedDict
from datetime import date

# Reproductibilité
SEED = 42

# Période de référence
START_DATE = date(2023, 1, 1)
END_DATE = date(2025, 12, 31)

# Volumes
NUM_SUPPLIERS = 25
NUM_PARTS = 40
NUM_PURCHASE_ORDERS = 2000

# Taux d'anomalies (appliqué par le module anomalies.py)
ANOMALY_RATE = 0.04  # 4 %

# Répartition des familles de pièces
PART_FAMILIES = {
    "SUSPENSION": ["spring", "damper", "control_arm", "ball_joint", "bushing"],
    "ELECTRIC_POWERTRAIN": ["stator", "rotor", "inverter", "cooling_system"],
}

# Valeurs métier fixes (cohérentes avec le schéma SQL)
SUPPLIER_TYPES = ["TIER1", "TIER2", "RAW_MATERIAL"]
RISK_PROFILES = ["LOW", "MEDIUM", "HIGH"]
CRITICALITY_LEVELS = ["LOW", "MEDIUM", "HIGH"]
INCIDENT_TYPES = ["DIMENSIONAL", "MATERIAL", "FUNCTIONAL", "PACKAGING"]
SEVERITY_LEVELS = ["MINOR", "MAJOR", "CRITICAL"]

# Pays fournisseurs plausibles pour un contexte automobile
SUPPLIER_COUNTRIES = ["FR", "DE", "ES", "IT", "PL", "CZ", "RO", "MA", "TR", "CN", "KR", "JP", "MX"]

# Fourchettes de prix unitaire réalistes par sous-catégorie (EUR)
# Devise fixée à EUR en v1 : voir ADR-0002, fx_rate hors périmètre
PART_PRICE_RANGES = {
    # SUSPENSION
    "bushing": (3.0, 15.0),
    "ball_joint": (15.0, 45.0),
    "spring": (20.0, 70.0),
    "control_arm": (40.0, 120.0),
    "damper": (50.0, 150.0),
    # ELECTRIC_POWERTRAIN
    "cooling_system": (60.0, 180.0),
    "rotor": (80.0, 220.0),
    "stator": (100.0, 280.0),
    "inverter": (200.0, 450.0),
}

# Retard de livraison selon le profil de risque fournisseur
DELIVERY_DELAY_RANGES_BY_RISK = {
    "LOW":    {"jitter_days": (-2, 3),  "major_delay_prob": 0.05},
    "MEDIUM": {"jitter_days": (-2, 8),  "major_delay_prob": 0.15},
    "HIGH":   {"jitter_days": (-2, 20), "major_delay_prob": 0.35},
}
MAJOR_DELAY_EXTRA_DAYS = (10, 30)  # ajout en cas de "retard important"

PARTIAL_DELIVERY_RATE = 0.15  # 15 % des commandes livrées en 2 fois

IN_PROGRESS_WINDOW_DAYS = 21  # commandes proches de END_DATE potentiellement "en cours"
IN_PROGRESS_PROBABILITY = 0.40

# Fréquence d'incidents qualité selon le profil de risque fournisseur
INCIDENT_PROBABILITY_BY_RISK = {
    "LOW": 0.03,
    "MEDIUM": 0.08,
    "HIGH": 0.18,
}

ORPHAN_INCIDENT_RATE = 0.10  # incidents supplémentaires sans po_id (ex. audit qualité)

SEVERITY_WEIGHTS = OrderedDict([
    ("MINOR", 0.60),
    ("MAJOR", 0.30),
    ("CRITICAL", 0.10),
])

QUANTITY_AFFECTED_RATIO_RANGE = (0.05, 0.40)  # part de la quantité livrée touchée

# Simulation du stock (inventory_snapshots)
DAILY_CONSUMPTION_RANGE = (2, 15)   # unités consommées par jour, tirées une fois par pièce
SAFETY_STOCK_DAYS_COVERAGE = 10     # safety_stock = consommation_quotidienne x ce nombre de jours
INITIAL_STOCK_DAYS_COVERAGE = 15    # stock de départ = consommation_quotidienne x ce nombre de jours
