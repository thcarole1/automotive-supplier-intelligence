# ADR-0001 : Choix de PostgreSQL local plutôt qu'un socle cloud d'emblée

## Contexte

Les deux projets précédents du portfolio (*Electric Mobility Platform*, *EV Powertrain Manufacturing Analytics*) démontrent déjà une maîtrise du cloud AWS (S3, Glue/Athena, Lambda, MWAA, MSK, EMR Serverless) et de l'infrastructure as code (Terraform). Ce troisième projet vise à combler un trou différent du portfolio : la modélisation de données relationnelle/transactionnelle (star schema, SCD2, multi-facts de type ERP/achats), absente des deux projets précédents. Il faut décider de l'infrastructure de stockage/traitement pour ce projet.

## Décision

Le socle v1 du projet repose entièrement sur des services locaux : PostgreSQL en conteneur Docker pour le stockage, dbt pour la transformation, Airflow en local (Docker) pour l'orchestration, Power BI en connexion directe pour la restitution. Aucun service cloud managé n'est utilisé à ce stade. Un volet AWS est explicitement mis hors périmètre v1, à réévaluer dans une session dédiée une fois le socle local terminé.

## Pourquoi

- Le cloud AWS est déjà démontré de façon approfondie ailleurs dans le portfolio ; le répéter ici diluerait le signal plutôt que de le renforcer.
- L'objectif différenciant de ce projet est la modélisation relationnelle (star schema, SCD2), un sujet orthogonal au choix d'infrastructure cloud vs local. Le local permet de s'y concentrer sans coût ni complexité additionnelle.
- Alternative envisagée : Snowflake ou Postgres managé (RDS) dès le départ, écartée car elle introduirait une dépendance de coût et de configuration cloud sans apporter de valeur différenciante pour cette v1.
- Alternative envisagée : SQLite pour simplifier encore, écartée car PostgreSQL est le standard de facto en environnement ERP/achats réel et supporte nativement les contraintes et types nécessaires au modèle (SCD2, clés étrangères, fenêtrage).

## Conséquences

- Le projet est reproductible localement via `docker compose up`, sans dépendance à un compte cloud ni coût associé.
- Une migration cloud éventuelle (si validée en session dédiée) nécessitera un ADR spécifique et n'est pas anticipée dans les choix de modélisation actuels.
- Le README doit préciser explicitement ce choix pour éviter toute ambiguïté en entretien sur l'absence de cloud dans ce projet précis.
