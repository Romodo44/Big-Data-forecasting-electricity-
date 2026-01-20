from pyspark.sql import SparkSession
from pyspark.sql.functions import col, min as smin, max as smax

spark = (SparkSession.builder
         .appName("debug-bronze")
         .master("spark://spark-master:7077")
         .getOrCreate())

elec = spark.read.parquet("/opt/lakehouse/bronze/electricity")
w = spark.read.parquet("/opt/lakehouse/bronze/weather")

print("=== ELEC columns ===", elec.columns)
elec.printSchema()
print("=== ELEC sample ===")
elec.show(5, truncate=False)

# essaie ces deux colonnes possibles
for c in ["ts_hour", "ts_utc"]:
    if c in elec.columns:
        print("ELEC ts stats for", c)
        elec.select(smin(col(c)), smax(col(c))).show(truncate=False)
        elec.filter(col(c).isNull()).show(5, truncate=False)

print("=== WEATHER columns ===", w.columns)
w.printSchema()
print("=== WEATHER sample ===")
w.show(5, truncate=False)

for c in ["ts_hour", "ts_utc"]:
    if c in w.columns:
        print("WEATHER ts stats for", c)
        w.select(smin(col(c)), smax(col(c))).show(truncate=False)
        w.filter(col(c).isNull()).show(5, truncate=False)

spark.stop()
