# Appendices

## Appendix A: Technical Specifications

### A.1 System Requirements
- **Hardware Requirements**
  - CPU: 4+ cores, 2.5 GHz or higher
  - RAM: 16GB minimum
  - Storage: 500GB SSD
  - Network: 1Gbps Ethernet

- **Software Requirements**
  - Operating System: Linux/Windows Server 2019+
  - Python 3.8+
  - PostgreSQL 13+
  - Node.js 14+

### A.2 Database Schema
```sql
-- Users Table
CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(256) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    role VARCHAR(20) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Energy Consumption Table
CREATE TABLE energy_consumption (
    consumption_id SERIAL PRIMARY KEY,
    device_id VARCHAR(50) NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    power_usage FLOAT NOT NULL,
    voltage FLOAT,
    current FLOAT,
    power_factor FLOAT
);

-- Predictions Table
CREATE TABLE predictions (
    prediction_id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP NOT NULL,
    predicted_usage FLOAT NOT NULL,
    confidence_score FLOAT,
    model_version VARCHAR(20)
);
```

## Appendix B: API Documentation

### B.1 REST API Endpoints
```python
# Authentication
POST /api/auth/login
POST /api/auth/logout
POST /api/auth/register

# Energy Data
GET /api/energy/consumption
POST /api/energy/consumption
GET /api/energy/predictions
GET /api/energy/optimization

# User Management
GET /api/users
PUT /api/users/{user_id}
DELETE /api/users/{user_id}
```

### B.2 API Response Formats
```json
{
    "status": "success",
    "data": {
        "timestamp": "2024-03-20T10:00:00Z",
        "consumption": 150.5,
        "unit": "kWh"
    },
    "message": "Data retrieved successfully"
}
```

## Appendix C: Machine Learning Models

### C.1 Model Specifications
- **Energy Consumption Predictor**
  - Algorithm: LSTM Neural Network
  - Input Features: 10
  - Hidden Layers: 2
  - Output: 24-hour forecast
  - Accuracy: 92%

- **Anomaly Detector**
  - Algorithm: Isolation Forest
  - Features: 8
  - Detection Rate: 94.5%
  - False Positive Rate: 2.1%

### C.2 Model Training Parameters
```python
model_params = {
    'lstm_units': 64,
    'dropout_rate': 0.2,
    'batch_size': 32,
    'epochs': 100,
    'validation_split': 0.2
}
```

## Appendix D: Security Implementation

### D.1 Password Hashing
```python
def hash_password(password: str) -> str:
    salt = os.urandom(32)
    key = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt,
        100000
    )
    return salt + key
```

### D.2 JWT Token Structure
```json
{
    "header": {
        "alg": "HS256",
        "typ": "JWT"
    },
    "payload": {
        "user_id": "123",
        "role": "admin",
        "exp": 1735689600
    }
}
```

## Appendix E: User Interface Mockups

### E.1 Dashboard Layout
```
+------------------+------------------+
|     Header       |    User Info    |
+------------------+------------------+
|                  |                  |
|   Energy Graph   |  Consumption    |
|                  |    Stats        |
|                  |                  |
+------------------+------------------+
|                  |                  |
|   Predictions    |  Optimization   |
|                  |    Plans        |
|                  |                  |
+------------------+------------------+
```

### E.2 Color Scheme
- Primary: #2196F3 (Blue)
- Secondary: #4CAF50 (Green)
- Accent: #FFC107 (Yellow)
- Background: #FFFFFF (White)
- Text: #212121 (Dark Gray)

## Appendix F: Test Cases

### F.1 Unit Tests
```python
def test_energy_prediction():
    predictor = EnergyPredictor()
    result = predictor.predict_next_24h()
    assert len(result) == 24
    assert all(isinstance(x, float) for x in result)

def test_anomaly_detection():
    detector = AnomalyDetector()
    data = generate_test_data()
    anomalies = detector.detect(data)
    assert isinstance(anomalies, list)
    assert all(isinstance(x, bool) for x in anomalies)
```

### F.2 Integration Tests
```python
def test_data_flow():
    processor = DataProcessor()
    predictor = EnergyPredictor()
    data = processor.get_latest_data()
    predictions = predictor.predict(data)
    assert predictions is not None
    assert len(predictions) > 0
```

## Appendix G: Deployment Configuration

### G.1 Docker Configuration
```dockerfile
FROM python:3.8-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "app.py"]
```

### G.2 Environment Variables
```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=sems_db
DB_USER=admin
DB_PASSWORD=****

JWT_SECRET=****
API_KEY=****

LOG_LEVEL=INFO
DEBUG=False
```

## Appendix H: Performance Metrics

### H.1 System Performance
- Response Time: < 200ms
- Throughput: 1000 requests/second
- CPU Usage: < 60%
- Memory Usage: < 70%

### H.2 Database Performance
- Query Time: < 50ms
- Connection Pool: 100
- Cache Hit Ratio: 85%
- Index Usage: 90%

## Appendix I: Error Codes

### I.1 HTTP Status Codes
- 200: Success
- 400: Bad Request
- 401: Unauthorized
- 403: Forbidden
- 404: Not Found
- 500: Internal Server Error

### I.2 Custom Error Codes
```python
ERROR_CODES = {
    'E001': 'Invalid input data',
    'E002': 'Database connection failed',
    'E003': 'Model prediction failed',
    'E004': 'Authentication failed',
    'E005': 'Authorization failed'
}
```

## Appendix J: Maintenance Procedures

### J.1 Backup Procedures
```bash
# Database Backup
pg_dump -U admin sems_db > backup_$(date +%Y%m%d).sql

# File System Backup
tar -czf backup_$(date +%Y%m%d).tar.gz /app/data
```

### J.2 Update Procedures
```bash
# System Update
git pull origin main
pip install -r requirements.txt
python manage.py migrate
systemctl restart sems
``` 