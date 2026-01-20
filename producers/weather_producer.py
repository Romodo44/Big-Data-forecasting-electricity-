import os, json
import requests
from kafka import KafkaProducer

KAFKA_BOOTSTRAP = os.getenv("KAFKA_BOOTSTRAP", "kafka:9092")
TOPIC = os.getenv("WEATHER_TOPIC", "weather.events")

CITY = os.getenv("CITY", "Paris")
LAT = float(os.getenv("LAT", "48.8566"))
LON = float(os.getenv("LON", "2.3522"))

START_DATE = os.getenv("START_DATE", "2024-01-01")
END_DATE   = os.getenv("END_DATE",   "2024-12-31")

producer = KafkaProducer(
    bootstrap_servers=KAFKA_BOOTSTRAP,
    value_serializer=lambda v: json.dumps(v).encode("utf-8"),
)

url = (
    "https://archive-api.open-meteo.com/v1/archive"
    f"?latitude={LAT}&longitude={LON}"
    f"&start_date={START_DATE}&end_date={END_DATE}"
    "&hourly=temperature_2m,precipitation,wind_speed_10m"
    "&timezone=UTC"
)

r = requests.get(url, timeout=120).json()
hours = r["hourly"]["time"]
temps = r["hourly"]["temperature_2m"]
rain  = r["hourly"]["precipitation"]
wind  = r["hourly"]["wind_speed_10m"]

for t, temp, rain_mm, wind_ms in zip(hours, temps, rain, wind):
    event = {
        "city": CITY,
        "ts_utc": t + ":00Z",
        "temp_c": temp,
        "rain_mm": rain_mm,
        "wind_ms": wind_ms,
        "source": "open_meteo_archive",
    }
    producer.send(TOPIC, event)

producer.flush()
print(f"WEATHER SENT: {len(hours)}")
