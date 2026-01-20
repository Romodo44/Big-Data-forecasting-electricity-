from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col, to_timestamp, date_trunc, hour, dayofweek,
    when, max as spark_max
)

spark = (
    SparkSession.builder
    .appName("silver-gold-join")
    .master("spark://spark-master:7077")
    .getOrCreate()
)

# ========= READ BRONZE ELECTRICITY =========
elec = spark.read.parquet("/opt/lakehouse/bronze/electricity")

elec_silver = (
    elec
    .withColumn("ts", to_timestamp("ts_utc"))   # ISO avec +00:00 => OK
    .withColumn("ts_hour", date_trunc("hour", col("ts")))
    .select("zone", "ts_hour", "load_mw")
)

# 30min -> 1h (mean MW)
elec_1h = (
    elec_silver
    .groupBy("zone", "ts_hour")
    .avg("load_mw")
    .withColumnRenamed("avg(load_mw)", "load_mw")
)

# drop last incomplete hour
max_ts = elec_1h.select(spark_max("ts_hour")).collect()[0][0]
elec_1h = elec_1h

# ========= READ BRONZE WEATHER =========
weather = spark.read.parquet("/opt/lakehouse/bronze/weather")

weather_silver = (
    weather
    .withColumn("ts", to_timestamp("ts_utc"))
    .withColumn("ts_hour", date_trunc("hour", col("ts")))
    .select("city", "ts_hour", "temp_c", "rain_mm", "wind_ms")
)



# ========= FEATURES =========
gold = (
    elec_1h.alias("e")
    .join(
        weather_silver.alias("w"),
        col("e.ts_hour") == col("w.ts_hour"),
        how="left"
    )
    .select(
        col("e.ts_hour").alias("ts_hour"),
        col("e.zone"),
        col("e.load_mw"),
        col("w.city"),
        col("w.temp_c"),
        col("w.rain_mm"),
        col("w.wind_ms"),
    )
)

gold = gold.filter(col("ts_hour").isNotNull())

# ========= WRITE GOLD =========
(
    gold.write
    .mode("overwrite")
    .parquet("/opt/lakehouse/gold/timeseries")
)

print("GOLD WITH WEATHER WRITTEN")
spark.stop()
