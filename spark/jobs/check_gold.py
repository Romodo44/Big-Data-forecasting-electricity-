from pyspark.sql import SparkSession

spark = SparkSession.builder.getOrCreate()

df = spark.read.parquet("/opt/lakehouse/gold/timeseries")

df.printSchema()
df.show(10, truncate=False)

spark.stop()
