import json
import datetime
import paho.mqtt.client as mqtt
from pyspark.sql import SparkSession
import pyspark.sql.functions as F
import pyspark.sql.types as T
import threading
import time
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# MQTT Settings
MQTT_HOST = "mqtt_broker"
MQTT_PORT = 1883
MQTT_TOPIC = "sensors"
PARQUET_TABLE_PATH = "/app/parquet_tables/sensor_data"
SENSORS_JSON_PATH = "/app/sensors.json"
MASTER_TABLE_PATH = "/app/parquet_tables/sensor_master"

# Spark Session
spark = SparkSession.builder.appName("MQTTToParquet").getOrCreate()

# Load sensor metadata
with open(SENSORS_JSON_PATH) as f:
    sensor_metadata = json.load(f)

# Create Master Data Table (Sensor Metadata)
def create_master_table():
    master_data = []
    for sensor_id, data in sensor_metadata.items():
        master_data.append((
            sensor_id,
            data.get('lat'),
            data.get('lng'),
            data.get('unit'),
            data.get('type'),
            data.get('range')[0],
            data.get('range')[1],
            data.get('description')
        ))

    master_schema = T.StructType([
        T.StructField("id", T.StringType()),
        T.StructField("lat", T.IntegerType()),
        T.StructField("lng", T.IntegerType()),
        T.StructField("unit", T.StringType()),
        T.StructField("type", T.StringType()),
        T.StructField("range_min", T.IntegerType()),
        T.StructField("range_max", T.IntegerType()),
        T.StructField("description", T.StringType())
    ])

    master_df = spark.createDataFrame(master_data, master_schema)

    (
        master_df
        .withColumn("load_ts", F.current_timestamp())
        .coalesce(1)
        .write.format("parquet")
        .mode("overwrite")
        .save(MASTER_TABLE_PATH)
    )

create_master_table()

# Read and show the master data table
try:
    sensor_master_df = spark.read.parquet(MASTER_TABLE_PATH)
    for row in sensor_master_df.take(10):
        logger.info(f"Sensor Data Row: {row}")
    logger.info("Sensor data table displayed")

except Exception as e:
    logger.exception(f"Error reading master data table: {e}")

# Define schema for streaming data
schema = T.StructType([
    T.StructField("id", T.StringType()),
    T.StructField("dt", T.StringType()),
    T.StructField("value", T.IntegerType())
])

BATCH_SIZE = 150  # Number of messages to batch
BATCH_INTERVAL = 30  # Time interval (seconds) to batch

message_buffer = []
start_time = time.time()
last_write_time = time.time()

def write_parquet_batch(spark, message_buffer):
    if message_buffer:
        try:
            df = spark.createDataFrame(message_buffer, schema)

            # Broadcast join with master data
            enriched_df = (
                df
                .join(F.broadcast(sensor_master_df.select("id", "range_min", "range_max")), "id", "left")
                .withColumn(
                    "in_range", 
                    (F.col("value") >= F.col("range_min")) & (F.col("value") <= F.col("range_max"))
                )
                .withColumn("load_ts", F.current_timestamp())
                .withColumn("load_date", F.to_date(F.col("load_ts")))
                .select("id", "load_date", "load_ts", "value", "in_range", "dt")
            )

            enriched_df.coalesce(1).write.mode("append").partitionBy("id", "load_date").parquet(PARQUET_TABLE_PATH)
            logger.info(f"Number of files written into the table: {len(message_buffer)}")

            message_buffer.clear()
        except Exception as e:
            logger.exception(f"Error writing batch: {e}")

def on_message(client, userdata, msg):
    global last_write_time
    global start_time
    try:
        payload = json.loads(msg.payload.decode("utf-8"))
        message_buffer.append(payload)

        if len(message_buffer) >= BATCH_SIZE or (time.time() - last_write_time) >= BATCH_INTERVAL:
            write_parquet_batch(spark, message_buffer)
            last_write_time = time.time()  # Reset the timer

        if (time.time() - start_time) >= 200:
            logger.info("Sttoping the client after 1 min!")
            client.disconnect()

            # Read a sample of the parquet data table
            try:
                sensor_data_df = spark.read.parquet(PARQUET_TABLE_PATH)
                for row in sensor_data_df.take(10):
                    logger.info(f"Sensor Data Row: {row}")
                logger.info("Sensor data table displayed")
            except Exception as e:
                logger.exception(f"Error reading parquet data table: {e}")

    except Exception as e:
        logger.exception(f"Error processing message: {e}")

client = mqtt.Client()
client.connect(MQTT_HOST, MQTT_PORT, 60)
client.on_message = on_message
client.subscribe(MQTT_TOPIC)
client.loop_forever()
