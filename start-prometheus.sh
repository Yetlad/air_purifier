#!/bin/bash

# Create a temporary prometheus config
cat > /tmp/prometheus.yml << EOF
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'air-purifier'
    static_configs:
      - targets: ['host.docker.internal:8080']
    scrape_interval: 30s
    metrics_path: '/metrics'
EOF

# Run Prometheus with the config
docker run -d --name prometheus \
  --add-host=host.docker.internal:host-gateway \
  -p 9090:9090 \
  -v /tmp/prometheus.yml:/etc/prometheus/prometheus.yml:ro \
  prom/prometheus:v2.45.0

echo "Prometheus should be starting at http://localhost:9090"