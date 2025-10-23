# QUICK START GUIDE

## 🚀 Get Started in 5 Minutes

### Option 1: Run Locally (Fastest)

1. **Install Python 3.11+** (if not already installed)

2. **Clone and setup**
```bash
git clone https://github.com/yourusername/waste-monitor-api.git
cd waste-monitor-api
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. **Run the application**
```bash
uvicorn app.main:app --reload
```

4. **Test it!**
Open http://localhost:8000/docs in your browser

---

### Option 2: Run with Docker (Recommended)

1. **Install Docker Desktop**
   - Download from https://www.docker.com/products/docker-desktop/

2. **Build and run**
```bash
git clone https://github.com/yourusername/waste-monitor-api.git
cd waste-monitor-api
docker build -t waste-monitor-api .
docker run -d -p 8000:8000 --name waste-monitor waste-monitor-api
```

3. **Test it!**
```bash
curl http://localhost:8000/
```

---

## 🧪 Run Tests

```bash
# Activate virtual environment first
source venv/bin/activate  # Windows: venv\Scripts\activate

# Run tests
pytest tests/ -v

# With coverage
pytest tests/ -v --cov=app --cov-report=html
```

---

## 📸 Taking Screenshots for Assignment

### 1. Jenkins Pipeline Screenshots Needed:

**Screenshot 1: Jenkins Dashboard**
- Navigate to http://localhost:8080
- Show your pipeline job

**Screenshot 2: Pipeline Configuration**
- Click on your job → Configure
- Show the Pipeline section with Jenkinsfile

**Screenshot 3: Successful Build**
- Run the pipeline
- Capture the Stage View with all stages green ✓

**Screenshot 4: Console Output**
- Click on a build number → Console Output
- Show test execution and Docker build

**Screenshot 5: Docker Hub**
- Login to Docker Hub
- Show your pushed image

### 2. Test Results Screenshots:

**Screenshot 6: Local Test Run**
```bash
pytest tests/ -v
```
Capture the terminal output

**Screenshot 7: Coverage Report**
```bash
pytest tests/ -v --cov=app --cov-report=html
open htmlcov/index.html  # Capture the coverage webpage
```

**Screenshot 8: API Documentation**
- Open http://localhost:8000/docs
- Capture the interactive API documentation

**Screenshot 9: Docker Build**
```bash
docker build -t waste-monitor-api .
```
Capture the build output

**Screenshot 10: Running Container**
```bash
docker ps
curl http://localhost:8000/
```
Capture both commands

---

## 📝 Commands Cheat Sheet

### Development
```bash
# Start API
uvicorn app.main:app --reload

# Run tests
pytest tests/ -v

# Code quality
flake8 app/ --max-line-length=100
```

### Docker
```bash
# Build
docker build -t waste-monitor-api .

# Run
docker run -d -p 8000:8000 --name waste-monitor waste-monitor-api

# Logs
docker logs waste-monitor

# Stop
docker stop waste-monitor && docker rm waste-monitor
```

### Testing API
```bash
# Health check
curl http://localhost:8000/

# Submit sensor data
curl -X POST http://localhost:8000/api/sensor-data \
  -H "Content-Type: application/json" \
  -d '{"bin_id":"BIN-001","fill_level":75,"temperature":22,"weight_kg":10,"location":"ICU"}'

# Get all bins
curl http://localhost:8000/api/bins

# Get alerts
curl http://localhost:8000/api/alerts
```

---

## ⚡ Troubleshooting

**Problem: Port 8000 already in use**
```bash
# Find and kill the process
# macOS/Linux
lsof -ti:8000 | xargs kill -9

# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

**Problem: Module not found**
```bash
# Make sure virtual environment is activated
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

**Problem: Docker build fails**
```bash
docker system prune -a
docker build --no-cache -t waste-monitor-api .
```

---

## 📚 Next Steps

1. ✅ Run the application locally
2. ✅ Run all tests successfully  
3. ✅ Build Docker image
4. ✅ Set up Jenkins/GitHub Actions
5. ✅ Take screenshots
6. ✅ Write your report

See `SETUP_GUIDE.md` for detailed instructions!
