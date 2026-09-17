# ADR-0003 : Retrait de dim_plant du périmètre v1

## Contexte

Le cahier des charges initial prévoit une dimension `dim_plant` parmi les marts dbt (`dim_supplier`, `dim_part`, `dim_plant`, `dim_date`). Or aucune des 6 tables sources du périmètre v1 (`suppliers`, `parts`, `purchase_orders`, `deliveries`, `quality_incidents`, `inventory_snapshots`) ne contient d'information sur des usines ou sites de production. Il faut décider comment traiter cette incohérence entre le cahier des charges initial et les données réellement disponibles.

## Décision

`dim_plant` est retirée du périmètre v1. Les marts se limitent à `dim_supplier`, `dim_part` et `dim_date`. Une extension future vers une notion d'usine (multi-sites, consommation par pays) reste possible, déjà documentée comme piste d'extension dans le README.

## Pourquoi

- Aucune table source ne porte cette information : créer `dim_plant` maintenant nécessiterait soit une dimension vide ou fictive sans lien réel avec les faits, soit l'ajout d'une 7ᵉ table source.
- Le périmètre de 6 tables a déjà été explicitement acté et documenté comme volontairement minimal (voir ADR-0002). Ajouter une table supplémentaire maintenant reviendrait sur cette décision sans raison nouvelle suffisante.
- Alternative envisagée : ajouter une table `plants` avec un rattachement aux `purchase_orders` ou aux `inventory_snapshots`. Écartée en v1 car elle complexifierait le modèle sans réel apport pour le narratif du projet (modélisation relationnelle achats/qualité/stock, pas gestion multi-sites).

## Conséquences

- Le star schema final compte 3 dimensions (`dim_supplier`, `dim_part`, `dim_date`) au lieu des 4 initialement prévues.
- Le README doit être mis à jour pour refléter ce périmètre final de marts, en cohérence avec la piste d'extension déjà notée.
- Si une v2 introduit une notion d'usine, elle nécessitera un nouvel ADR et une nouvelle table source, pas seulement l'ajout d'une dimension.
