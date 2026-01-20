from urllib.parse import urlencode
import pandas as pd
import json
from kafka import KafkaProducer

# Kafka
KAFKA_BOOTSTRAP = "kafka:9092"
TOPIC = "electricity.events"

ZONE = "FR"

# Source ODRE (celle qui marche chez toi)
base_url = (
    "https://odre.opendatasoft.com/api/v2/catalog/datasets/"
    "consommation-quotidienne-brute/exports/csv"
)

params = {
    "where": (
        "date_heure >= '2024-01-01T00:00:00+00:00' "
        "AND date_heure <= '2024-12-31T23:00:00+00:00'"
    ),
    "order_by": "date_heure"
}

url = f"{base_url}?{urlencode(params)}"
print("FETCH:", url)

df = pd.read_csv(url, sep=";")
df["date_heure"] = pd.to_datetime(df["date_heure"], utc=True)

df = df[[
    "date_heure",
    "consommation_brute_electricite_rte",
    "statut_rte"
]].dropna()

producer = KafkaProducer(
    bootstrap_servers=KAFKA_BOOTSTRAP,
    value_serializer=lambda v: json.dumps(v).encode("utf-8"),
)

for _, row in df.iterrows():
    event = {
            "event_type": "electricity",
            "zone": "FR",
            "ts_utc": row["date_heure"].strftime("%Y-%m-%dT%H:%M:%SZ"),
            "load_mw": float(row["consommation_brute_electricite_rte"]),
        }

    producer.send(TOPIC, event)

producer.flush()
print(f"ELEC SENT: {len(df)}")
