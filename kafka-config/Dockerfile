FROM bitnami/kafka:latest

# Ajouter JMX Exporter
COPY jmx_exporter.jar /opt/bitnami/kafka/jmx_prometheus_javaagent.jar
COPY kafka-jmx-exporter-config.yml /opt/bitnami/kafka/kafka-jmx-exporter-config.yml

# Exposer le port de JMX Exporter
EXPOSE 5555

# Configurer le démarrage de Kafka pour inclure l'agent JMX Exporter
ENV KAFKA_OPTS="-javaagent:/opt/bitnami/kafka/jmx_prometheus_javaagent.jar=5555:/opt/bitnami/kafka/kafka-jmx-exporter-config.yml"
