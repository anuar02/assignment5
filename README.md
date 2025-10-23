# Medical Waste Monitoring API

IoT-based system for tracking and managing medical waste in healthcare facilities.

## 🎯 Project Overview

This REST API receives sensor data from IoT-enabled waste bins, processes it in real-time, and generates alerts when bins require collection. The system helps healthcare facilities optimize waste management, ensure regulatory compliance, and enhance safety.

## 🚀 Features

- **Real-time Monitoring**: Track fill levels, temperature, and weight of waste bins
- **Automated Alerts**: Generate alerts when bins reach critical levels
- **RESTful API**: Easy integration with IoT devices and frontend applications
- **Data Analytics**: Calculate statistics and trends
- **Docker Support**: Fully containerized for easy deployment
- **CI/CD Pipeline**: Automated testing and deployment with Jenkins

## 📋 Requirements

- Python 3.11+
- Docker (for containerization)
- Jenkins (for CI/CD)

## 🛠️ Installation

### Local Development

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/waste-monitor-api.git
cd waste-monitor-api
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Run the application**
```bash
uvicorn app.main:app --reload
```

5. **Access the API**
- API: http://localhost:8000
- Interactive Docs: http://localhost:8000/docs
- Alternative Docs: http://localhost:8000/redoc

### Docker Deployment

1. **Build Docker image**
```bash
docker build -t waste-monitor-api .
```

2. **Run container**
```bash
docker run -d -p 8000:8000 --name waste-monitor waste-monitor-api
```

3. **View logs**
```bash
docker logs waste-monitor
```

## 🧪 Running Tests

### Run all tests
```bash
pytest tests/ -v
```

### Run with coverage report
```bash
pytest tests/ -v --cov=app --cov-report=html
```

### Run specific test file
```bash
pytest tests/test_sensor_handler.py -v
```

### Code quality check
```bash
flake8 app/ --max-line-length=100
```

## 📚 API Endpoints

### Health Check
```
GET /
```
Returns API health status

### Submit Sensor Data
```
POST /api/sensor-data
```
**Request Body:**
```json
{
  "bin_id": "BIN-ICU-001",
  "fill_level": 75.5,
  "temperature": 22.0,
  "weight_kg": 12.3,
  "location": "ICU-Floor3"
}
```

### Get All Bins
```
GET /api/bins
```
Returns list of all waste bins with current status

### Get Bin Details
```
GET /api/bins/{bin_id}
```
Returns detailed information for specific bin

### Get Active Alerts
```
GET /api/alerts
```
Returns list of active alerts

### Mark Bin as Emptied
```
POST /api/bins/{bin_id}/empty
```
Updates bin status after collection

### Get System Statistics
```
GET /api/statistics
```
Returns overall system statistics

## 🔄 CI/CD Pipeline

The project uses Jenkins for automated CI/CD:

1. **Code Checkout**: Pull latest code from repository
2. **Setup Environment**: Create Python virtual environment
3. **Code Quality**: Run flake8 checks
4. **Unit Tests**: Execute pytest with coverage
5. **Build Docker Image**: Create containerized application
6. **Test Docker Image**: Verify container functionality
7. **Push to Registry**: Upload to Docker Hub (on main branch)
8. **Deploy**: Deploy to test environment (on main branch)

### Jenkins Setup

1. Install Jenkins and required plugins:
   - Docker Pipeline
   - Git
   - Pipeline

2. Configure credentials:
   - Add Docker Hub credentials with ID `dockerhub-credentials`

3. Create new Pipeline job:
   - Point to your repository
   - Use `Jenkinsfile` from repository

## 📊 Project Structure

```
waste-monitor-api/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── models.py            # Pydantic models
│   ├── sensor_handler.py    # Sensor data processing
│   ├── alert_generator.py   # Alert logic
│   └── database.py          # Data storage
├── tests/
│   ├── __init__.py
│   ├── test_sensor_handler.py
│   ├── test_alert_generator.py
│   └── test_api_endpoints.py
├── Dockerfile               # Container configuration
├── Jenkinsfile             # CI/CD pipeline
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## 🎨 Example Usage

### Python Script
```python
import requests

# Submit sensor data
data = {
    "bin_id": "BIN-ER-001",
    "fill_level": 85.0,
    "temperature": 22.5,
    "weight_kg": 15.2,
    "location": "Emergency-Room"
}

response = requests.post(
    "http://localhost:8000/api/sensor-data",
    json=data
)
print(response.json())
```

### cURL
```bash
curl -X POST "http://localhost:8000/api/sensor-data" \
     -H "Content-Type: application/json" \
     -d '{
       "bin_id": "BIN-ER-001",
       "fill_level": 85.0,
       "temperature": 22.5,
       "weight_kg": 15.2,
       "location": "Emergency-Room"
     }'
```

## 🔐 Security Considerations

- Input validation using Pydantic models
- Non-root user in Docker container
- Health checks for container monitoring
- Environment variables for sensitive data

## 📈 Future Enhancements

- [ ] PostgreSQL database integration
- [ ] WebSocket support for real-time updates
- [ ] User authentication and authorization
- [ ] Kubernetes deployment manifests
- [ ] Prometheus metrics export
- [ ] Grafana dashboards
- [ ] Email/SMS notifications

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

## 📝 License

This project is part of an academic assignment for Applied Software Development.

## 👥 Authors

- Your Name - Medical Waste Monitoring Team

## 📧 Contact

For questions or support, please contact: your.email@example.com

## 🙏 Acknowledgments

- Assignment 5: DevOps and CI/CD
- Course: Applied Software Development Project
- Topic: IoT-based Medical Waste Monitoring
