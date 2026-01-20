from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, current_timestamp
from pyspark.sql.types import StructType, StructField, StringType, DoubleType

spark = (
    SparkSession.builder
    .appName("weather-bronze")
    .master("spark://spark-master:7077")
    .getOrCreate()
)

schema = StructType([
    StructField("city", StringType(), True),
    StructField("ts_utc", StringType(), True),
    StructField("temp_c", DoubleType(), True),
    StructField("rain_mm", DoubleType(), True),
    StructField("wind_ms", DoubleType(), True),
])

df = (
    spark.readStream
    .format("kafka")
    .option("kafka.bootstrap.servers", "kafka:9092")
    .option("subscribe", "weather.events")
    .option("startingOffsets", "earliest")
    .load()
)

parsed = (
    df.selectExpr("CAST(value AS STRING) as value_str")
      .withColumn("ingest_ts", current_timestamp())
      .withColumn("json", from_json(col("value_str"), schema))
      .select("ingest_ts", "value_str", "json.*")
)

(
    parsed.writeStream
    .format("parquet")
    .option("path", "/opt/lakehouse/bronze/weather")
    .option("checkpointLocation", "/opt/lakehouse/checkpoints/bronze_weather")
    .outputMode("append")
    .start()
    .awaitTermination()
)
