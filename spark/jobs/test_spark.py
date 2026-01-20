from pyspark.sql import SparkSession
from pyspark.sql.functions import col, lit

spark = (
    SparkSession.builder
    .appName("spark-docker-test")
    .master("spark://spark-master:7077")
    .getOrCreate()
)

df = spark.createDataFrame([(1, "a"), (2, "b"), (3, "c")], ["id", "val"])
df = df.withColumn("src", lit("docker")).filter(col("id") >= 2)

out_path = "/opt/lakehouse/test_out_parquet"
df.write.mode("overwrite").parquet(out_path)

print("WROTE:", out_path)
print("COUNT:", df.count())
df.show(truncate=False)

spark.stop()
