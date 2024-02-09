FROM bitnami/spark:3.5

WORKDIR .

RUN pip install influxdb-client

USER root

# Script pour exécuter les tâches Spark
COPY ./entrypoint.sh /opt/entrypoint.sh
RUN chmod +x /opt/entrypoint.sh

# Définir le script comme point d'entrée
ENTRYPOINT ["/opt/entrypoint.sh"]
