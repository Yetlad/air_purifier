# Air Purifier Monitoring System

A complete monitoring solution for air purifier sensor data using Docker Compose with PostgreSQL, FastAPI, Prometheus, and Grafana.

## Services

- **RabbitMQ** (Port 5672, Management: 15672): Message broker for sensor data
- **Dummy Server** (Port 8080): FastAPI server that consumes sensor data from RabbitMQ
- **PostgreSQL** (Port 5432): Database for storing sensor readings
- **Prometheus** (Port 9090): Metrics collection and monitoring
- **Grafana** (Port 3000): Data visualization dashboard
- **Adminer** (Port 8081): Database management interface for PostgreSQL

## Architecture

The system follows a message-driven architecture:
1. Sensor data is published to RabbitMQ queue
2. Python server consumes messages from RabbitMQ
3. Data is processed and stored in PostgreSQL
4. Prometheus scrapes metrics from the server
5. Grafana visualizes the data

## Quick Start

1. **Start the main services:**
   ```bash
   docker-compose up --build -d
   ```

2. **Start Prometheus (macOS workaround):**
   ```bash
   ./start-prometheus.sh
   ```

3. **Access the services:**
   - RabbitMQ Management: http://localhost:15672 (admin/admin)
   - Grafana Dashboard: http://localhost:3000 (admin/admin)
   - Prometheus: http://localhost:9090
   - Adminer (Database UI): http://localhost:8081
   - API Health Check: http://localhost:8080/health
   - Latest Sensor Data: http://localhost:8080/latest-data

## RabbitMQ Management

Access the RabbitMQ Management UI at http://localhost:15672:
- **Username**: admin
- **Password**: admin

From the management interface, you can:
- View the `sensor_data` queue
- Publish test messages manually
- Monitor message rates and queue depth
- View consumer connections

### Publishing Messages via RabbitMQ UI

1. Go to the "Queues" tab
2. Click on the `sensor_data` queue
3. Expand "Publish message"
4. Set Payload:
   ```json
   {"co2": 850, "humidity": 45.5, "temperature": 23.2}
   ```
5. Click "Publish message"

## Database Access

Access the PostgreSQL database via Adminer at http://localhost:8081:
- **System**: PostgreSQL
- **Server**: postgres
- **Username**: postgres
- **Password**: password
- **Database**: air_purifier

## API Endpoints

### GET /health
Health check endpoint

### GET /latest-data
Get the most recent sensor reading

### POST /sensor-data
Publish sensor data to RabbitMQ queue
```json
{
  "co2": 850,
  "humidity": 45.5,
  "temperature": 23.2
}
```
Note: This endpoint publishes data to RabbitMQ, which is then consumed by the server and stored in the database.

### GET /metrics
Prometheus metrics endpoint

## Database Schema

The system stores sensor data in PostgreSQL:
```sql
CREATE TABLE sensor_data (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    co2_ppm DECIMAL(6,2) NOT NULL,
    humidity_percent DECIMAL(5,2) NOT NULL,
    temperature_celsius DECIMAL(5,2) NOT NULL
);
```

## Metrics

The system exposes the following Prometheus metrics:
- `air_purifier_co2_ppm`: Current CO2 levels in PPM
- `air_purifier_humidity_percent`: Current humidity percentage
- `air_purifier_temperature_celsius`: Current temperature in Celsius
- `air_purifier_data_received_total`: Total data points received

## Sample Data

The system automatically generates realistic sensor data every 30 seconds:
1. Data is published to RabbitMQ queue
2. Consumer picks up the message
3. Data is processed and stored in PostgreSQL
4. Metrics are updated in Prometheus

## Testing

### Option 1: Send test data via API
```bash
curl -X POST http://localhost:8080/sensor-data \
  -H "Content-Type: application/json" \
  -d '{"co2": 850, "humidity": 45.5, "temperature": 23.2}'
```

### Option 2: Publish directly to RabbitMQ Management UI
1. Open http://localhost:15672
2. Login with admin/admin
3. Go to Queues → sensor_data
4. Publish a message with JSON payload

### Option 3: Use Python script to publish
```python
import pika
import json

connection = pika.BlockingConnection(pika.URLParameters('amqp://admin:admin@localhost:5672/'))
channel = connection.channel()
channel.queue_declare(queue='sensor_data', durable=True)

message = json.dumps({"co2": 850, "humidity": 45.5, "temperature": 23.2})
channel.basic_publish(exchange='', routing_key='sensor_data', body=message)
connection.close()
```

Check metrics:
```bash
curl http://localhost:8080/metrics
```

## Grafana Dashboard

The system includes a pre-configured dashboard showing:
- Real-time CO2, humidity, and temperature readings
- Historical trends and charts
- Color-coded thresholds for air quality monitoring

Login to Grafana at http://localhost:3000 with admin/admin to view the dashboard.