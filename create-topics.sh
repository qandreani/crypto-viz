#!/bin/bash

# Attendez que Kafka soit prêt avant de créer les topics
echo "Attente de Kafka pour démarrer..."
while [ ! nc -z kafka 9092 ]; do 
  sleep 1 
done

echo "Kafka démarré"

# Créez les topics
kafka-topics.sh --create --topic topic1 --bootstrap-server kafka:9092 --partitions 1 --replication-factor 1
kafka-topics.sh --create --topic topic2 --bootstrap-server kafka:9092 --partitions 1 --replication-factor 1

echo "Topics créés"
