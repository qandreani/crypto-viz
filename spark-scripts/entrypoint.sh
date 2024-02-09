#!/bin/bash
set -e

pip install influxdb-client

# Lancement des scripts Spark en parallèle
echo "Lancement du script Spark : cryptocurrency-treatment.py en arrière-plan"
/opt/bitnami/spark/bin/spark-submit --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0 /opt/spark-scripts/cryptocurrency-treatment.py &

# Affichage d'un message indiquant le début de l'attente
echo "Attente de 30 secondes avant de démarrer le script Spark : influxdb-writer.py en arrière-plan"

# Attendre 30 secondes
sleep 30

echo "Lancement du script Spark : influxdb-writer.py en arrière-plan"
/opt/bitnami/spark/bin/spark-submit --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0 /opt/spark-scripts/influxdb-writer.py &

# Garder le conteneur en vie (si nécessaire)
tail -f /dev/null

executor = 3
vCore = 3
giga = 2

