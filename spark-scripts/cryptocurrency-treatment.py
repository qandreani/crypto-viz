from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, explode
from pyspark.sql.types import StructType, StructField, StringType, FloatType, IntegerType, LongType, MapType


def main():
    spark = SparkSession.builder \
        .appName("CryptoStream") \
        .master("local[2]") \
        .getOrCreate()

    crypto_schema = StructType([
        StructField("iso", StringType()),
        StructField("name", StringType()),
        StructField("slug", StringType()),
        StructField("change", StructType([
            StructField("percent", FloatType()),
            StructField("value", FloatType())
        ])),
        StructField("ohlc", StructType([
            StructField("o", FloatType()),
            StructField("h", FloatType()),
            StructField("l", FloatType()),
            StructField("c", FloatType())
        ])),
        StructField("circulatingSupply", FloatType()),
        StructField("marketCap", FloatType()),
        StructField("ts", LongType()),
        StructField("src", StringType())
    ])

    data_schema = StructType([
        StructField("statusCode", IntegerType()),
        StructField("message", StringType()),
        StructField("data", MapType(StringType(), crypto_schema))
    ])

    kafka_stream_df = spark.readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", "kafka:9092") \
        .option("subscribe", "topic1") \
        .option("failOnDataLoss", "false") \
        .load()

    # Debugging
    #kafka_stream_df.writeStream.foreachBatch(lambda df, epoch_id: df.show()).start().awaitTermination()

    parsed_data = kafka_stream_df \
        .selectExpr("CAST(key AS STRING)", "CAST(value AS STRING)") \
        .withColumn("value", from_json(col("value"), data_schema)) \
        .select(
            "key",
            explode(col("value.data")).alias("crypto_key", "crypto_value")
        )

    filtered_data = parsed_data \
        .select(
            "key",
            "crypto_key",
            "crypto_value.name",
            col("crypto_value.ohlc.c").alias("current_price"),
            "crypto_value.ts"
        )

    try:
        query = filtered_data.selectExpr("CAST(key AS STRING)", "to_json(struct(*)) AS value") \
            .writeStream \
            .format("kafka") \
            .option("kafka.bootstrap.servers", "kafka:9092") \
            .option("topic", "topic2") \
            .option("checkpointLocation", "/opt/spark-checkpoints") \
            .outputMode("append") \
            .start()

        query.awaitTermination()

    except Exception as e:
        print("Une erreur s'est produite : ", e)

    spark.stop()


if __name__ == "__main__":
    main()
