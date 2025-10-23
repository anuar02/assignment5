# Practical Report: CI/CD Pipeline for IoT Medical Waste Monitoring System

**Student Name:** [Your Name]  
**Course:** Applied Software Development Project  
**Assignment:** Assignment 5 - DevOps and CI/CD  
**Date:** [Date]  
**Project:** Medical Waste Monitoring API

---

## 1. Project Overview

This report documents the implementation of a CI/CD pipeline for the IoT-based Medical Waste Monitoring system. The project demonstrates the application of DevOps practices including containerization, automated testing, and continuous integration/deployment.

### 1.1 Project Description

The Medical Waste Monitoring API is a REST API service that:
- Receives real-time sensor data from IoT-enabled waste bins
- Processes data to determine bin status and generate alerts
- Provides endpoints for monitoring and management
- Implements automated testing and deployment workflows

### 1.2 Technology Stack

- **Programming Language:** Python 3.11
- **Web Framework:** FastAPI
- **Testing:** Pytest
- **Containerization:** Docker
- **CI/CD:** Jenkins / GitHub Actions
- **Version Control:** Git/GitHub

---

## 2. Implementation Steps

### 2.1 Project Structure Setup

[INSERT SCREENSHOT 1: Project directory structure]

The project follows a standard Python application structure:
```
waste-monitor-api/
├── app/                    # Application source code
├── tests/                  # Unit and integration tests
├── Dockerfile             # Container configuration
├── Jenkinsfile           # CI/CD pipeline definition
├── requirements.txt      # Python dependencies
└── docker-compose.yml    # Multi-container setup
```

**Key Files Created:**
- `main.py`: FastAPI application with REST endpoints
- `models.py`: Pydantic data models for validation
- `sensor_handler.py`: Business logic for sensor data processing
- `alert_generator.py`: Alert creation and management logic
- `database.py`: In-memory data storage

### 2.2 Dockerization

[INSERT SCREENSHOT 2: Dockerfile content]

The Dockerfile was created with the following features:
- **Base Image:** Python 3.11-slim for minimal size
- **Security:** Non-root user for running the application
- **Health Check:** Automatic container health monitoring
- **Multi-stage potential:** Can be optimized for production

**Docker Build Process:**
```bash
docker build -t waste-monitor-api .
```

[INSERT SCREENSHOT 3: Docker build output]

**Docker Run:**
```bash
docker run -d -p 8000:8000 --name waste-monitor waste-monitor-api
```

[INSERT SCREENSHOT 4: Docker container running (docker ps output)]

**Testing Docker Container:**
```bash
curl http://localhost:8000/
```

[INSERT SCREENSHOT 5: API response from Docker container]

### 2.3 Unit Testing Implementation

A comprehensive test suite was created with three main test files:

**test_sensor_handler.py** - Tests for sensor data processing logic:
- `test_determine_bin_status()`: Validates status classification
- `test_check_temperature_alert()`: Tests temperature validation
- `test_process_sensor_data()`: Validates data processing pipeline
- `test_validate_sensor_data()`: Tests input validation

**test_alert_generator.py** - Tests for alert generation:
- `test_generate_alert_if_needed()`: Alert creation logic
- `test_create_alert()`: Alert structure validation
- `test_should_escalate_alert()`: Escalation rules

**test_api_endpoints.py** - Integration tests for API:
- Tests all REST endpoints
- Validates request/response formats
- Tests error handling

[INSERT SCREENSHOT 6: Running pytest]

**Test Execution:**
```bash
pytest tests/ -v
```

[INSERT SCREENSHOT 7: Pytest output showing all tests passing]

**Coverage Report:**
```bash
pytest tests/ --cov=app --cov-report=html
```

[INSERT SCREENSHOT 8: Coverage report HTML page]

The test coverage achieved was **XX%**, covering all critical functionality.

### 2.4 CI/CD Pipeline Setup

#### Option A: Jenkins Pipeline

[INSERT SCREENSHOT 9: Jenkins dashboard]

**Jenkins Installation:**
Jenkins was installed using Docker for portability:
```bash
docker run -d -p 8080:8080 -p 50000:50000 \
  -v jenkins_home:/var/jenkins_home \
  --name jenkins jenkins/jenkins:lts
```

**Plugin Installation:**
The following plugins were installed:
- Docker Pipeline
- Git Plugin  
- Pipeline
- Pipeline: Stage View

[INSERT SCREENSHOT 10: Jenkins installed plugins]

**Credentials Configuration:**
Docker Hub credentials were configured in Jenkins:
- Credentials ID: `dockerhub-credentials`
- Type: Username with password

[INSERT SCREENSHOT 11: Jenkins credentials configuration]

**Pipeline Configuration:**

[INSERT SCREENSHOT 12: Jenkins job configuration]

The Jenkinsfile defines a 7-stage pipeline:

1. **Checkout**: Pull code from repository
2. **Setup Python Environment**: Create virtual environment and install dependencies
3. **Code Quality Check**: Run flake8 linting
4. **Run Unit Tests**: Execute pytest with coverage
5. **Build Docker Image**: Create container image
6. **Test Docker Image**: Verify container functionality
7. **Push to Docker Hub**: Upload image to registry (main branch only)
8. **Deploy**: Deploy to test environment (main branch only)

[INSERT SCREENSHOT 13: Jenkins pipeline stage view - all green]

[INSERT SCREENSHOT 14: Jenkins console output showing tests passing]

**Pipeline Execution Results:**
- Build Number: #X
- Duration: X minutes
- Status: SUCCESS ✓
- All tests passed: XX/XX

#### Option B: GitHub Actions (Alternative)

[Alternative section if using GitHub Actions instead]

[INSERT SCREENSHOT: GitHub Actions workflow]

---

## 3. Challenges and Solutions

### Challenge 1: Docker Socket Permission Issues

**Problem:** Jenkins couldn't access Docker daemon when building images.

**Error Message:**
```
permission denied while trying to connect to the Docker daemon socket
```

**Solution:**
Added Jenkins user to docker group:
```bash
sudo usermod -aG docker jenkins
sudo systemctl restart jenkins
```

### Challenge 2: Import Path Issues in Tests

**Problem:** Pytest couldn't find the `app` module when running tests.

**Solution:**
Ensured proper project structure and ran pytest from project root directory. The project structure with `app/` as a package and `__init__.py` files resolved the issue.

### Challenge 3: Port Conflicts

**Problem:** Port 8000 was already in use during local testing.

**Solution:**
```bash
lsof -ti:8000 | xargs kill -9  # macOS/Linux
```
Or used alternative port: `uvicorn app.main:app --port 8001`

---

## 4. Deployment Verification

### 4.1 Docker Hub Verification

[INSERT SCREENSHOT 15: Docker Hub showing pushed image]

The image was successfully pushed to Docker Hub and is publicly accessible:
- Repository: `yourusername/waste-monitor-api`
- Tags: `latest`, `build-XX`
- Size: XXX MB

### 4.2 API Functionality Verification

[INSERT SCREENSHOT 16: API documentation (Swagger UI)]

All API endpoints were tested and verified working:

✅ `GET /` - Health check  
✅ `POST /api/sensor-data` - Submit sensor readings  
✅ `GET /api/bins` - List all bins  
✅ `GET /api/bins/{bin_id}` - Get bin details  
✅ `GET /api/alerts` - Get alerts  
✅ `POST /api/bins/{bin_id}/empty` - Mark bin emptied  
✅ `GET /api/statistics` - System statistics  

### 4.3 End-to-End Test

[INSERT SCREENSHOT 17: Manual API testing showing request and response]

Example test scenario:
1. Submit sensor data with 85% fill level
2. Verify alert is generated
3. Mark bin as emptied
4. Verify alert is resolved

All steps executed successfully, demonstrating the complete workflow.

---

## 5. Repository Information

**GitHub Repository:** https://github.com/yourusername/waste-monitor-api

The repository contains:
- Complete source code
- Test suite
- Dockerfile and Jenkinsfile
- Documentation (README, SETUP_GUIDE, QUICKSTART)
- GitHub Actions workflow (if applicable)

[INSERT SCREENSHOT 18: GitHub repository overview]

---

## 6. Conclusions

### 6.1 Key Achievements

✅ Successfully implemented a fully functional REST API for IoT medical waste monitoring  
✅ Created comprehensive test suite with XX% code coverage  
✅ Containerized application using Docker with security best practices  
✅ Implemented automated CI/CD pipeline with 8 stages  
✅ Achieved successful automated testing and deployment  
✅ Documented entire process for reproducibility  

### 6.2 Learning Outcomes

Through this project, I gained practical experience with:

1. **DevOps Practices:** Understanding the importance of automation in software development lifecycle
2. **Docker Containerization:** Creating portable, consistent application environments
3. **CI/CD Pipelines:** Implementing automated testing and deployment workflows
4. **Testing:** Writing comprehensive unit and integration tests
5. **Git Workflow:** Managing code versions and collaboration practices

### 6.3 Benefits of DevOps for Research Projects

This project demonstrates how DevOps practices benefit research projects:

- **Reproducibility:** Docker ensures consistent environments across different systems
- **Quality Assurance:** Automated testing catches bugs early
- **Rapid Iteration:** CI/CD enables quick testing of new features
- **Collaboration:** Clear processes make it easier for team members to contribute
- **Documentation:** Automated processes are self-documenting

### 6.4 Future Improvements

Potential enhancements for the project:

1. **Database Integration:** Replace in-memory storage with PostgreSQL
2. **Kubernetes Deployment:** Add K8s manifests for production deployment
3. **Monitoring:** Integrate Prometheus and Grafana for metrics
4. **Security:** Add authentication and authorization
5. **Performance:** Implement caching and optimization
6. **Notifications:** Add email/SMS alerts for critical events

---

## 7. References

- FastAPI Documentation: https://fastapi.tiangolo.com/
- Docker Documentation: https://docs.docker.com/
- Jenkins Pipeline Documentation: https://www.jenkins.io/doc/book/pipeline/
- Pytest Documentation: https://docs.pytest.org/
- Assignment 5 Guidelines: DevOps and CI/CD Course Materials

---

## Appendices

### Appendix A: Complete Dockerfile

[Include Dockerfile content]

### Appendix B: Complete Jenkinsfile

[Include Jenkinsfile content]

### Appendix C: Test Coverage Summary

[Include coverage report summary table]

### Appendix D: API Endpoint Documentation

[Include list of all endpoints with descriptions]

---

**Note:** All screenshots mentioned with [INSERT SCREENSHOT X] should be replaced with actual screenshots taken during implementation.
