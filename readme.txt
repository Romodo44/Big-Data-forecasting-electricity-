With the dataset I put already on GitHub you just need to:

1-Launch Docker Desktop
2-START THE MACHINE:docker compose up -d
3-Look at the results:http://localhost:8501
4-Stop everythin:docker compose stop


If you want to start from the beginning and execute everything:
1-Reset:
docker compose down -v
docker system prune -f
rmdir /s /q lakehouse
mkdir lakehouse
docker compose up -d

2-DATA:
Run bronze:
docker compose exec spark-master /opt/spark/bin/spark-submit --conf spark.jars.ivy=/tmp/.ivy2 --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.1 /opt/spark/jobs/streaming_bronze.py

Run gold:
docker compose exec spark-master /opt/spark/bin/spark-submit /opt/spark/jobs/silver_gold.py

3-PREDICTIONS:

Packages:
docker compose exec --user root spark-master pip3 install pandas pyarrow joblib xgboost scikit-learn
Creating predictions:
docker compose exec spark-master python3 /opt/spark/jobs/prediction/train_xgb.py

4-RESULTS:
http://localhost:8501


TESTS:
CHECK KFKA AND SPARK RUN:
http://localhost:8080

CHECK BRONZE DATA:
docker compose exec spark-master /opt/spark/bin/spark-submit /opt/spark/jobs/debug_bronze.py

CHECK GOLD DATA:
docker compose exec spark-master /opt/spark/bin/spark-submit /opt/spark/jobs/check_gold.py

CHECK PREDICTION:
docker compose exec spark-master python3 /opt/spark/jobs/prediction/test_xgb.py
