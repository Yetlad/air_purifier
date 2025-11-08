import asyncio
import random
import time
import json
import threading
from datetime import datetime
from typing import Dict, Any
import os
import asyncpg
import pika
from fastapi import FastAPI, HTTPException
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from fastapi.responses import Response
import uvicorn

app = FastAPI(title="Air Purifier Monitor")

# Prometheus metrics
co2_gauge = Gauge('air_purifier_co2_ppm', 'CO2 levels in PPM')
humidity_gauge = Gauge('air_purifier_humidity_percent', 'Humidity percentage')
temperature_gauge = Gauge('air_purifier_temperature_celsius', 'Temperature in Celsius')
data_received_counter = Counter('air_purifier_data_received_total', 'Total data points received')

# Database connection
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5432/air_purifier")
RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://admin:admin@localhost:5672/")
QUEUE_NAME = "sensor_data"

async def get_db_connection():
    return await asyncpg.connect(DATABASE_URL)

async def process_sensor_data(co2: float, humidity: float, temperature: float):
    """Process and store sensor data"""
    try:
        # Update Prometheus metrics
        co2_gauge.set(co2)
        humidity_gauge.set(humidity)
        temperature_gauge.set(temperature)
        data_received_counter.inc()
        
        # Store in database
        conn = await get_db_connection()
        await conn.execute("""
            INSERT INTO sensor_data (timestamp, co2_ppm, humidity_percent, temperature_celsius)
            VALUES ($1, $2, $3, $4)
        """, datetime.now(), co2, humidity, temperature)
        await conn.close()
        
        print(f"Processed data: CO2={co2:.1f}ppm, Humidity={humidity:.1f}%, Temp={temperature:.1f}°C")
    except Exception as e:
        print(f"Error processing sensor data: {e}")

def rabbitmq_consumer():
    """RabbitMQ consumer running in a separate thread"""
    while True:
        try:
            # Connect to RabbitMQ
            connection = pika.BlockingConnection(pika.URLParameters(RABBITMQ_URL))
            channel = connection.channel()
            
            # Declare queue
            channel.queue_declare(queue=QUEUE_NAME, durable=True)
            
            print(f"[*] Waiting for messages in queue '{QUEUE_NAME}'. To exit press CTRL+C")
            
            def callback(ch, method, properties, body):
                try:
                    data = json.loads(body)
                    co2 = float(data.get("co2", 0))
                    humidity = float(data.get("humidity", 0))
                    temperature = float(data.get("temperature", 0))
                    
                    # Process data in async context
                    asyncio.run(process_sensor_data(co2, humidity, temperature))
                    
                    ch.basic_ack(delivery_tag=method.delivery_tag)
                    print(f"[✓] Received from RabbitMQ: CO2={co2:.1f}ppm, Humidity={humidity:.1f}%, Temp={temperature:.1f}°C")
                except Exception as e:
                    print(f"Error processing message: {e}")
                    ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
            
            channel.basic_qos(prefetch_count=1)
            channel.basic_consume(queue=QUEUE_NAME, on_message_callback=callback)
            
            channel.start_consuming()
            
        except pika.exceptions.AMQPConnectionError as e:
            print(f"RabbitMQ connection error: {e}. Retrying in 5 seconds...")
            time.sleep(5)
        except Exception as e:
            print(f"RabbitMQ consumer error: {e}. Retrying in 5 seconds...")
            time.sleep(5)

@app.on_event("startup")
async def startup_event():
    # Start RabbitMQ consumer in a separate thread
    consumer_thread = threading.Thread(target=rabbitmq_consumer, daemon=True)
    consumer_thread.start()
    print("[*] RabbitMQ consumer thread started")
    
    # Start background task to generate dummy data (optional, for testing)
    asyncio.create_task(generate_dummy_data())

async def generate_dummy_data():
    """Generate realistic sensor data every 30 seconds and publish to RabbitMQ"""
    await asyncio.sleep(10)  # Wait for RabbitMQ to be ready
    
    while True:
        try:
            # Generate realistic sensor data
            co2 = random.uniform(400, 1200)  # Normal indoor CO2 range
            humidity = random.uniform(30, 70)  # Normal humidity range
            temperature = random.uniform(18, 28)  # Normal room temperature
            
            # Publish to RabbitMQ instead of directly storing
            try:
                connection = pika.BlockingConnection(pika.URLParameters(RABBITMQ_URL))
                channel = connection.channel()
                channel.queue_declare(queue=QUEUE_NAME, durable=True)
                
                message = json.dumps({
                    "co2": co2,
                    "humidity": humidity,
                    "temperature": temperature
                })
                
                channel.basic_publish(
                    exchange='',
                    routing_key=QUEUE_NAME,
                    body=message,
                    properties=pika.BasicProperties(delivery_mode=2)  # Make message persistent
                )
                
                connection.close()
                print(f"[→] Published to RabbitMQ: CO2={co2:.1f}ppm, Humidity={humidity:.1f}%, Temp={temperature:.1f}°C")
            except Exception as e:
                print(f"Error publishing to RabbitMQ: {e}")
            
        except Exception as e:
            print(f"Error generating data: {e}")
        
        await asyncio.sleep(30)

@app.post("/sensor-data")
async def receive_sensor_data(data: Dict[str, Any]):
    """Endpoint to receive sensor data and publish to RabbitMQ"""
    try:
        co2 = float(data.get("co2", 0))
        humidity = float(data.get("humidity", 0))
        temperature = float(data.get("temperature", 0))
        
        # Publish to RabbitMQ
        connection = pika.BlockingConnection(pika.URLParameters(RABBITMQ_URL))
        channel = connection.channel()
        channel.queue_declare(queue=QUEUE_NAME, durable=True)
        
        message = json.dumps({
            "co2": co2,
            "humidity": humidity,
            "temperature": temperature
        })
        
        channel.basic_publish(
            exchange='',
            routing_key=QUEUE_NAME,
            body=message,
            properties=pika.BasicProperties(delivery_mode=2)
        )
        
        connection.close()
        
        return {"status": "success", "message": "Data published to RabbitMQ"}
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error publishing data: {str(e)}")

@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.get("/latest-data")
async def get_latest_data():
    """Get the latest sensor readings"""
    try:
        conn = await get_db_connection()
        row = await conn.fetchrow("""
            SELECT * FROM sensor_data 
            ORDER BY timestamp DESC 
            LIMIT 1
        """)
        await conn.close()
        
        if row:
            return {
                "timestamp": row["timestamp"].isoformat(),
                "co2_ppm": row["co2_ppm"],
                "humidity_percent": row["humidity_percent"],
                "temperature_celsius": row["temperature_celsius"]
            }
        else:
            return {"message": "No data available"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)