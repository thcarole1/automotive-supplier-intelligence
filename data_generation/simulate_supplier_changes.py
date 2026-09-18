"""
Simule une évolution métier de quelques fournisseurs (dégradation du risque,
désactivation), pour donner un contenu réel au SCD2 de dim_supplier.

Usage manuel, hors du pipeline Airflow (voir README pour la justification).
Nécessite un dbt snapshot déjà exécuté au moins une fois avant ce script,
et un second dbt snapshot après, pour que le changement soit historisé.
"""

import logging
import random

from data_generation.config import SEED
from data_generation.db import get_connection

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

CHANGE_RATE = 0.15  # ~15 % des fournisseurs concernés
RISK_DEGRADATION = {
    "LOW": "MEDIUM",
    "MEDIUM": "HIGH",
    "HIGH": "HIGH",  # déjà au maximum, pas de dégradation possible
}


def main() -> None:
    random.seed(SEED)
    conn = get_connection()

    with conn.cursor() as cur:
        cur.execute("SELECT supplier_id, risk_profile FROM raw.suppliers")
        suppliers = cur.fetchall()

    num_changes = max(1, round(len(suppliers) * CHANGE_RATE))
    affected = random.sample(suppliers, num_changes)

    with conn.cursor() as cur:
        for supplier_id, risk_profile in affected:
            change_type = random.choice(["degrade_risk", "deactivate"])

            if change_type == "degrade_risk":
                new_risk = RISK_DEGRADATION[risk_profile]
                cur.execute(
                    "UPDATE raw.suppliers SET risk_profile = %s WHERE supplier_id = %s",
                    (new_risk, supplier_id),
                )
                logger.info(
                    "supplier_id=%d : risk_profile %s -> %s",
                    supplier_id, risk_profile, new_risk,
                )
            else:
                cur.execute(
                    "UPDATE raw.suppliers SET is_active = FALSE WHERE supplier_id = %s",
                    (supplier_id,),
                )
                logger.info("supplier_id=%d : is_active -> FALSE", supplier_id)

    conn.commit()
    conn.close()
    logger.info("Simulation terminée : %d fournisseur(s) modifié(s).", num_changes)


if __name__ == "__main__":
    main()
