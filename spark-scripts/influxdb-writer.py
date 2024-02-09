from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col
from pyspark.sql.types import StructType, StringType, DoubleType, LongType
import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS

bucket = "mybucket"
org = "myorg"
token = "mytoken"
url = "http://influxdb:8086"

spark = SparkSession.builder \
    .appName("Kafka-InfluxDB-Stream") \
    .getOrCreate()

# Define the schema for parsing the data
schema = StructType() \
    .add("crypto_key", StringType()) \
    .add("name", StringType()) \
    .add("current_price", DoubleType()) \
    .add("ts", LongType())

# Read from Kafka
df = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "kafka:9092") \
    .option("subscribe", "topic2") \
    .load()

print("Printing schema")
df.printSchema()

# Transform the data
parsed_df = df.selectExpr("CAST(value AS STRING)") \
    .select(from_json(col("value"), schema).alias("data")) \
    .select("data.*")

print("Printing parsed schema")
parsed_df.printSchema()

def write_to_influxdb(batch_df, epoch_id):
    try:
        records = [row.asDict() for row in batch_df.collect()]

        data_points = [{
            "measurement": "crypto_prices",
            "tags": {
                "crypto_key": record['crypto_key'],
                "name": record['name']
            },
            "ts": record['ts'] * 1000000,  # Convert to nanoseconds
            "fields": {
                "current_price": record['current_price']
            }
        } for record in records]

        client = influxdb_client.InfluxDBClient(
            url=url,
            token=token,
            org=org
        )

        write_api = client.write_api(write_options=SYNCHRONOUS)
        write_api.write(bucket=bucket, org=org, record=data_points)
    except Exception as e:
        print(f"Error writing to InfluxDB: {e}")
    finally:
        if 'write_api' in locals():
            write_api.close()
        if 'client' in locals():
            client.close()


query = parsed_df.writeStream.foreachBatch(write_to_influxdb).outputMode("append").start()

query.awaitTermination()

