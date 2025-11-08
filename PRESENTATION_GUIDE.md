# Air Purifier Monitoring System - Student Presentation Guide

## Project Overview
This project demonstrates a complete IoT monitoring solution for air quality sensors using modern containerized microservices architecture.

## What We Built

### 🎯 Problem Statement
- Need to monitor indoor air quality in real-time
- Track CO2 levels, humidity, and temperature from air purifiers
- Visualize data trends and set up alerts for poor air quality
- Store historical data for analysis

### 🏗️ System Architecture

```
Air Purifier Sensors → FastAPI Server → PostgreSQL Database
                                    ↓
                              Prometheus Metrics
                                    ↓
                              Grafana Dashboard
```

## Technical Components

### 1. **Dummy Sensor Server (FastAPI)**
- **Purpose**: Simulates real air purifier sensor data
- **Technology**: Python FastAPI (lightweight, fast)
- **Features**:
  - Generates realistic CO2 (400-1200 PPM), humidity (30-70%), temperature (18-28°C)
  - REST API endpoints for receiving sensor data
  - Prometheus metrics export
  - Health monitoring

### 2. **Database Layer (PostgreSQL)**
- **Purpose**: Persistent storage for sensor readings
- **Why PostgreSQL**: ACID compliance, time-series data handling
- **Schema**: Timestamped sensor readings with proper indexing
- **Data**: Pre-seeded with 24 hours of historical data (1440 data points)

### 3. **Metrics Collection (Prometheus)**
- **Purpose**: Time-series metrics collection and monitoring
- **Why Prometheus**: Industry standard, pull-based metrics, powerful querying
- **Metrics Collected**:
  - `air_purifier_co2_ppm`: Real-time CO2 levels
  - `air_purifier_humidity_percent`: Humidity readings
  - `air_purifier_temperature_celsius`: Temperature data
  - `air_purifier_data_received_total`: System health counter

### 4. **Visualization (Grafana)**
- **Purpose**: Real-time dashboards and alerting
- **Why Grafana**: Professional dashboards, alerting, multi-datasource support
- **Dashboard Features**:
  - Color-coded thresholds (Green: Good, Yellow: Warning, Red: Alert)
  - Real-time stat panels
  - Historical trend charts
  - Auto-refresh every 30 seconds

## Key Technical Decisions

### **Containerization with Docker**
- **Benefits**: Consistent environments, easy deployment, scalability
- **Images Used**: 
  - `python:3.11-alpine` (lightweight Python runtime)
  - `postgres:15-alpine` (minimal database)
  - `prom/prometheus:v2.45.0` (metrics collection)
  - `grafana/grafana:10.0.0` (visualization)

### **Microservices Architecture**
- **Separation of Concerns**: Each service has a single responsibility
- **Scalability**: Can scale components independently
- **Maintainability**: Easy to update individual services

### **RESTful API Design**
```bash
GET  /health           # System health check
GET  /latest-data      # Most recent sensor reading
POST /sensor-data      # Accept new sensor data
GET  /metrics          # Prometheus metrics endpoint
```

## Data Flow Demonstration

### 1. **Data Generation**
```python
# Realistic sensor simulation
co2 = random.uniform(400, 1200)      # Normal indoor range
humidity = random.uniform(30, 70)     # Comfortable range
temperature = random.uniform(18, 28)  # Room temperature
```

### 2. **Data Storage**
```sql
INSERT INTO sensor_data (timestamp, co2_ppm, humidity_percent, temperature_celsius)
VALUES (NOW(), 850.5, 45.2, 23.1);
```

### 3. **Metrics Export**
```
# HELP air_purifier_co2_ppm CO2 levels in PPM
# TYPE air_purifier_co2_ppm gauge
air_purifier_co2_ppm 850.5
```

## Live Demo Script

### **Step 1: Show System Status**
```bash
docker ps  # Show all running containers
curl http://localhost:8080/health  # Demonstrate API
```

### **Step 2: Send Test Data**
```bash
curl -X POST http://localhost:8080/sensor-data \
  -H "Content-Type: application/json" \
  -d '{"co2": 950, "humidity": 65, "temperature": 26}'
```

### **Step 3: Show Data Storage**
- Access latest data: `curl http://localhost:8080/latest-data`
- Show database contains the new reading

### **Step 4: Demonstrate Monitoring**
- Open Prometheus: http://localhost:9090
- Show metrics collection and queries
- Open Grafana: http://localhost:3000
- Navigate to Air Purifier Monitor dashboard
- Point out real-time updates and color coding

## Real-World Applications

### **Smart Building Management**
- Monitor air quality across office floors
- Automatic HVAC adjustments based on CO2 levels
- Energy optimization through data-driven decisions

### **Health & Safety Compliance**
- Ensure workplace air quality standards
- Alert systems for poor ventilation
- Historical reporting for regulatory compliance

### **IoT Device Integration**
- Easy integration with actual air purifier hardware
- Scalable to hundreds of sensors
- Cloud deployment ready

## Technical Challenges Solved

### **1. Data Persistence**
- Challenge: Reliable storage of time-series data
- Solution: PostgreSQL with proper indexing and data types

### **2. Real-time Monitoring**
- Challenge: Live data visualization
- Solution: Prometheus pull model + Grafana auto-refresh

### **3. System Reliability**
- Challenge: Container orchestration and health monitoring
- Solution: Docker Compose with health checks and restart policies

### **4. Cross-platform Compatibility**
- Challenge: macOS file permission issues with Docker volumes
- Solution: Alternative mounting strategies and runtime configuration

## Scalability Considerations

### **Horizontal Scaling**
- Add multiple sensor servers behind a load balancer
- Database read replicas for query performance
- Prometheus federation for multi-region monitoring

### **Performance Optimization**
- Database partitioning by time ranges
- Metrics retention policies
- Grafana query optimization

## Security Best Practices Implemented

- **Container Security**: Non-root users, minimal base images
- **Network Isolation**: Docker networks for service communication
- **Data Validation**: Input sanitization in API endpoints
- **Access Control**: Grafana authentication, database user permissions

## Conclusion

This project demonstrates:
- **Modern DevOps practices** with containerization
- **Microservices architecture** principles
- **Real-time data processing** and visualization
- **Production-ready monitoring** stack
- **Scalable IoT solution** design

The system is ready for production deployment and can easily integrate with real air purifier hardware or expand to monitor multiple environmental parameters.

## Questions to Anticipate

**Q: Why not use a simpler solution like just logging to files?**
A: This architecture provides real-time monitoring, alerting, historical analysis, and scales to enterprise needs.

**Q: How would you handle thousands of sensors?**
A: Implement load balancing, database sharding, Prometheus federation, and consider message queues for data ingestion.

**Q: What about data privacy and security?**
A: Add HTTPS/TLS, API authentication, data encryption at rest, and audit logging.

**Q: How do you ensure data accuracy?**
A: Implement sensor calibration, data validation rules, anomaly detection, and redundant sensors for critical measurements.