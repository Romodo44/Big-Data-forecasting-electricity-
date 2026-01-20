# ---------- TIME ----------
TIMEZONE = "UTC"
START_DATE = "2024-01-01"
END_DATE   = "2024-06-01"
# ---------- LOCALISATION ----------
ZONE = "FR"
CITY = "Paris"
# ---------- KAFKA ----------
KAFKA_BOOTSTRAP = "kafka:9092"
TOPIC_ELECTRICITY = "electricity.events"
TOPIC_WEATHER     = "weather.events"
# ---------- LAKEHOUSE ----------
LAKEHOUSE_ROOT = "/opt/lakehouse"
BRONZE_PATH = f"{LAKEHOUSE_ROOT}/bronze"
SILVER_PATH = f"{LAKEHOUSE_ROOT}/silver"
GOLD_DIR    = f"{LAKEHOUSE_ROOT}/gold"
GOLD_PATH   = f"{GOLD_DIR}/timeseries"  # dossier (dataset parquet)
# Sous-dossiers (recommandé)
BRONZE_ELEC_PATH    = f"{BRONZE_PATH}/electricity"
BRONZE_WEATHER_PATH = f"{BRONZE_PATH}/weather"
SILVER_ELEC_PATH    = f"{SILVER_PATH}/electricity"
SILVER_WEATHER_PATH = f"{SILVER_PATH}/weather"
# Clés/colonnes standardisées
COL_TS_HOUR = "ts_hour"
COL_ZONE    = "zone"
CHECKPOINT_ROOT = f"{LAKEHOUSE_ROOT}/checkpoints"
CHECKPOINT_ELEC    = f"{CHECKPOINT_ROOT}/bronze_electricity"
CHECKPOINT_WEATHER = f"{CHECKPOINT_ROOT}/bronze_weather"
# ---------- SPARK ----------
SPARK_APP_NAME = "bigdata-lakehouse"
SPARK_SHUFFLE_PARTITIONS = 200
SPARK_MASTER = "local[*]"  # change si cluster
SPARK_TIMEZONE = TIMEZONE
# ---------- API ----------
API_HOST = "0.0.0.0"
API_PORT = 8000
