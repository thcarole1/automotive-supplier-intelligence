# ADR-0002 : Périmètre volontairement minimal de 6 tables

## Contexte

La modélisation d'un système ERP/achats réel couvre potentiellement de nombreuses entités : fournisseurs, pièces, commandes, livraisons, qualité, stock, mais aussi contrats, taux de change, plans de production, factures, etc. Ce projet vise à démontrer une compétence de modélisation relationnelle/transactionnelle (star schema, SCD2, multi-facts), sans être un ERP complet. Il faut décider du périmètre fonctionnel exact à couvrir en v1.

## Décision

Le périmètre v1 est volontairement limité à 6 tables : `suppliers`, `parts`, `purchase_orders`, `deliveries`, `quality_incidents`, `inventory_snapshots`. Les entités `contracts`, `fx_rate` et `production_plan` sont explicitement exclues de la v1. Une extension reste possible si le temps le permet.

## Pourquoi

- Ces 6 tables suffisent à couvrir la chaîne causale complète visée par le projet (risque fournisseur menant à un retard de livraison menant à une rupture de stock, risque fournisseur menant à un incident qualité), qui est le narratif central à démontrer.
- Elles permettent de construire un star schema réaliste avec 4 dimensions et 4 facts, incluant un cas SCD2 sur `dim_supplier`, sans complexité superflue.
- Alternative envisagée : ajouter `fx_rate` pour gérer le multi-devises. Écartée car elle complexifierait les calculs de KPI sans démontrer une compétence de modélisation supplémentaire (c'est un sujet de conversion de données, pas de modélisation relationnelle).
- Alternative envisagée : ajouter `contracts` pour lier prix et conditions négociées aux commandes. Écartée en v1 car elle ajoute une dimension temporelle supplémentaire (durée de validité d'un contrat) qui aurait pu diluer le focus mis sur le SCD2 de `dim_supplier`.
- Un périmètre plus large risquerait de diluer le signal du projet (modélisation relationnelle) plutôt que de le renforcer, dans la même logique que l'exclusion de Spark, Kafka et Terraform (voir ADR-0001).

## Conséquences

- Les KPI financiers restent en devise d'origine, sans conversion (limite déjà documentée lors de la conception de `purchase_orders`).
- Aucune gestion de prix contractuels négociés à ce stade : `unit_price` sur `purchase_orders` est une valeur brute, pas dérivée d'un contrat.
- Une extension vers `contracts`, `fx_rate` ou `production_plan` nécessitera un ADR dédié si elle est décidée ultérieurement.
- Le README doit refléter ce périmètre volontairement minimal pour éviter toute impression d'oubli en entretien.
