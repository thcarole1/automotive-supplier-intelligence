# ADR-0004 : Fallback vers la version courante pour la jointure temporelle SCD2

## Contexte

Les facts référencent `dim_supplier` via `supplier_key` (clé de version SCD2), pour associer chaque fait à la version du fournisseur active à sa date. Le snapshot dbt (`snp_suppliers`) a été exécuté pour la première fois en septembre 2026, donc `dbt_valid_from` de la version initiale correspond à cette date, largement postérieure aux dates métier des commandes historiques (2023-2025). Une jointure temporelle stricte (date du fait comprise entre `valid_from` et `valid_to`) ne trouve donc aucune correspondance pour la totalité des faits déjà présents.

## Décision

Quand aucune version SCD2 n'est valide à la date du fait, celui-ci est associé à la version actuellement courante du fournisseur (`is_current = TRUE`), plutôt que de rester sans correspondance ou d'échouer.

## Pourquoi

- Le SCD2 ne capture l'historique qu'à partir du moment où il est activé ; il ne peut pas reconstituer rétroactivement un historique jamais enregistré. Ce n'est pas un défaut du modèle, mais une conséquence normale du choix de démarrer le SCD2 après la génération initiale des données.
- Alternative envisagée : abandonner la jointure temporelle et référencer `supplier_id` directement dans les facts. Écartée car elle viderait le SCD2 de son intérêt pédagogique dans les facts, alors que c'est un point clé du cahier des charges.
- Le fallback reste cohérent avec un vrai système en production : tout nouveau fait généré après l'activation du SCD2 bénéficiera d'une jointure temporelle correcte et significative.

## Conséquences

- Les facts historiques (générés avant l'activation du SCD2) reflètent tous la version actuelle du fournisseur, pas celle en vigueur à leur date réelle. C'est une limite connue, à mentionner dans le README.
- Un nouveau fait généré après un changement SCD2 (ex. une nouvelle commande passée après une dégradation de risque) bénéficiera d'une correspondance temporelle exacte, démontrant le mécanisme correctement.
