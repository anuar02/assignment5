# SETUP AND DEPLOYMENT GUIDE

## 📋 Table of Contents
1. [Prerequisites](#prerequisites)
2. [Local Development Setup](#local-development-setup)
3. [Running Tests](#running-tests)
4. [Docker Setup](#docker-setup)
5. [Jenkins CI/CD Setup](#jenkins-cicd-setup)
6. [GitHub Actions Setup](#github-actions-setup)
7. [Deployment Options](#deployment-options)
8. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Software
- **Python 3.11+**: [Download](https://www.python.org/downloads/)
- **Git**: [Download](https://git-scm.com/downloads)
- **Docker Desktop**: [Download](https://www.docker.com/products/docker-desktop/)

### Optional Software
- **Jenkins**: For CI/CD pipeline
- **Postman**: For API testing
- **VS Code**: Recommended IDE

---

## Local Development Setup

### Step 1: Clone Repository
```bash
git clone https://github.com/yourusername/waste-monitor-api.git
cd waste-monitor-api
```

### Step 2: Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 4: Run the Application
```bash
uvicorn app.main:app --reload
```

### Step 5: Test the API
Open your browser and navigate to:
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/

Or run the test script:
```bash
python test_api.py
```

---

## Running Tests

### Run All Tests
```bash
pytest tests/ -v
```

### Run with Coverage Report
```bash
pytest tests/ -v --cov=app --cov-report=html
```

View coverage report:
```bash
# Windows
start htmlcov/index.html

# macOS
open htmlcov/index.html

# Linux
xdg-open htmlcov/index.html
```

### Run Specific Test File
```bash
pytest tests/test_sensor_handler.py -v
pytest tests/test_alert_generator.py -v
pytest tests/test_api_endpoints.py -v
```

### Run Code Quality Checks
```bash
flake8 app/ --max-line-length=100 --exclude=__pycache__
```

---

## Docker Setup

### Build Docker Image
```bash
docker build -t waste-monitor-api .
```

### Run Docker Container
```bash
docker run -d -p 8000:8000 --name waste-monitor waste-monitor-api
```

### View Logs
```bash
docker logs waste-monitor
```

### Stop and Remove Container
```bash
docker stop waste-monitor
docker rm waste-monitor
```

### Using Docker Compose
```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

---

## Jenkins CI/CD Setup

### Step 1: Install Jenkins

**Option A: Docker (Recommended)**
```bash
docker run -d -p 8080:8080 -p 50000:50000 \
  -v jenkins_home:/var/jenkins_home \
  -v /var/run/docker.sock:/var/run/docker.sock \
  --name jenkins \
  jenkins/jenkins:lts
```

**Option B: Download from [jenkins.io](https://www.jenkins.io/download/)**

### Step 2: Initial Jenkins Setup

1. Access Jenkins at http://localhost:8080
2. Get initial admin password:
```bash
docker exec jenkins cat /var/jenkins_home/secrets/initialAdminPassword
```
3. Install suggested plugins
4. Create admin user

### Step 3: Install Required Plugins

Go to **Manage Jenkins → Manage Plugins → Available**

Install:
- Docker Pipeline
- Git Plugin
- Pipeline
- Pipeline: Stage View

### Step 4: Configure Docker Hub Credentials

1. Go to **Manage Jenkins → Manage Credentials**
2. Click **(global)** → **Add Credentials**
3. Select **Username with password**
4. ID: `dockerhub-credentials`
5. Username: Your Docker Hub username
6. Password: Your Docker Hub password
7. Click **OK**

### Step 5: Create Pipeline Job

1. Click **New Item**
2. Enter name: `waste-monitor-api`
3. Select **Pipeline**
4. Under **Pipeline** section:
   - Definition: **Pipeline script from SCM**
   - SCM: **Git**
   - Repository URL: Your GitHub repo URL
   - Script Path: `Jenkinsfile`
5. Click **Save**

### Step 6: Run Pipeline

1. Click **Build Now**
2. View console output for progress
3. Pipeline stages should all pass ✓

### Step 7: Configure Webhooks (Optional)

For automatic builds on code push:

1. In Jenkins job, check **GitHub hook trigger for GITScm polling**
2. In GitHub repo: **Settings → Webhooks → Add webhook**
3. Payload URL: `http://your-jenkins-url:8080/github-webhook/`
4. Content type: `application/json`
5. Select **Just the push event**

---

## GitHub Actions Setup

### Step 1: Create Repository Secrets

1. Go to your GitHub repository
2. Click **Settings → Secrets and variables → Actions**
3. Click **New repository secret**
4. Add the following secrets:
   - `DOCKER_USERNAME`: Your Docker Hub username
   - `DOCKER_PASSWORD`: Your Docker Hub password

### Step 2: Push Code with Workflow

The workflow file is already in `.github/workflows/ci-cd.yml`

```bash
git add .
git commit -m "Add CI/CD workflow"
git push origin main
```

### Step 3: View Workflow Status

1. Go to **Actions** tab in GitHub
2. See workflow runs and their status
3. Click on a workflow to see detailed logs

---

## Deployment Options

### Option 1: Local/VM Deployment

1. **Copy files to server**
```bash
scp -r waste-monitor-api user@server:/home/user/
```

2. **On the server**
```bash
cd waste-monitor-api
docker-compose up -d
```

### Option 2: Kubernetes Deployment (Optional)

Create `k8s-deployment.yaml`:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: waste-monitor-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: waste-monitor-api
  template:
    metadata:
      labels:
        app: waste-monitor-api
    spec:
      containers:
      - name: api
        image: yourusername/waste-monitor-api:latest
        ports:
        - containerPort: 8000
---
apiVersion: v1
kind: Service
metadata:
  name: waste-monitor-service
spec:
  selector:
    app: waste-monitor-api
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
  type: LoadBalancer
```

Deploy:
```bash
kubectl apply -f k8s-deployment.yaml
```

### Option 3: Cloud Deployment

**AWS ECS/Fargate:**
1. Push image to AWS ECR
2. Create ECS task definition
3. Create ECS service

**Google Cloud Run:**
```bash
gcloud run deploy waste-monitor-api \
  --image yourusername/waste-monitor-api:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

---

## Troubleshooting

### Issue: Tests Fail Locally

**Solution:**
```bash
# Reinstall dependencies
pip install --force-reinstall -r requirements.txt

# Clear pytest cache
rm -rf .pytest_cache
pytest tests/ -v
```

### Issue: Docker Build Fails

**Solution:**
```bash
# Clean Docker cache
docker system prune -a

# Rebuild without cache
docker build --no-cache -t waste-monitor-api .
```

### Issue: Jenkins Can't Access Docker

**Solution:**
```bash
# Add Jenkins user to docker group
sudo usermod -aG docker jenkins

# Restart Jenkins
sudo systemctl restart jenkins
```

### Issue: Port Already in Use

**Solution:**
```bash
# Find process using port 8000
# Windows
netstat -ano | findstr :8000

# macOS/Linux
lsof -i :8000

# Kill the process
# Windows
taskkill /PID <PID> /F

# macOS/Linux
kill -9 <PID>
```

### Issue: Import Errors

**Solution:**
```bash
# Make sure you're in the virtual environment
# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate

# Verify Python path
python -c "import sys; print(sys.path)"
```

---

## Common Commands Reference

### Git Commands
```bash
git add .
git commit -m "Your message"
git push origin main
git pull origin main
```

### Docker Commands
```bash
docker ps                    # List running containers
docker ps -a                 # List all containers
docker images                # List images
docker logs <container>      # View logs
docker exec -it <container> bash  # Enter container
docker stop <container>      # Stop container
docker rm <container>        # Remove container
docker rmi <image>          # Remove image
```

### Python Commands
```bash
pip freeze > requirements.txt    # Save dependencies
pip list                         # List installed packages
python -m pytest --version      # Check pytest version
python -m uvicorn --version     # Check uvicorn version
```

---

## Next Steps

1. ✅ Complete local development setup
2. ✅ Run all tests successfully
3. ✅ Build and test Docker image
4. ✅ Set up CI/CD pipeline (Jenkins or GitHub Actions)
5. ✅ Deploy to test environment
6. 📝 Write practical report with screenshots
7. 📤 Submit assignment

---

## Support

If you encounter any issues:

1. Check this troubleshooting guide
2. Review Docker/Jenkins logs
3. Verify all prerequisites are installed
4. Check that ports are not in use
5. Ensure virtual environment is activated

For more help, consult:
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Docker Documentation](https://docs.docker.com/)
- [Jenkins Documentation](https://www.jenkins.io/doc/)
- [Pytest Documentation](https://docs.pytest.org/)
