-- Create the sensor_data table
CREATE TABLE IF NOT EXISTS sensor_data (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    co2_ppm DECIMAL(6,2) NOT NULL,
    humidity_percent DECIMAL(5,2) NOT NULL,
    temperature_celsius DECIMAL(5,2) NOT NULL
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_sensor_data_timestamp ON sensor_data(timestamp);

-- Insert some initial seed data (last 24 hours)
INSERT INTO sensor_data (timestamp, co2_ppm, humidity_percent, temperature_celsius)
SELECT 
    NOW() - INTERVAL '1 minute' * generate_series(1, 1440),
    400 + (RANDOM() * 800)::DECIMAL(6,2),
    30 + (RANDOM() * 40)::DECIMAL(5,2),
    18 + (RANDOM() * 10)::DECIMAL(5,2)
FROM generate_series(1, 1440);