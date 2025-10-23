pipeline {
    agent any
    
    environment {
        // Docker Hub credentials (configure in Jenkins)
        DOCKER_HUB_CREDENTIALS = credentials('anuar-docker-hub')
        DOCKER_IMAGE_NAME = 'anuar-docker-hub/waste-monitor-api'
        DOCKER_IMAGE_TAG = "${BUILD_NUMBER}"
    }
    
    stages {
        stage('Checkout') {
            steps {
                echo 'Checking out code from repository...'
                checkout scm
            }
        }
        
        stage('Setup Python Environment') {
            steps {
                echo 'Setting up Python virtual environment...'
                sh '''
                    python3 -m venv venv
                    . venv/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements.txt
                '''
            }
        }
        
        stage('Code Quality Check') {
            steps {
                echo 'Running code quality checks with flake8...'
                sh '''
                    . venv/bin/activate
                    flake8 app/ --max-line-length=100 --exclude=__pycache__,venv --count --statistics || true
                '''
            }
        }
        
        stage('Run Unit Tests') {
            steps {
                echo 'Running unit tests with pytest...'
                sh '''
                    . venv/bin/activate
                    pytest tests/ -v --cov=app --cov-report=html --cov-report=term
                '''
            }
        }
        
        stage('Build Docker Image') {
            steps {
                echo 'Building Docker image...'
                sh '''
                    docker build -t ${DOCKER_IMAGE_NAME}:${DOCKER_IMAGE_TAG} .
                    docker tag ${DOCKER_IMAGE_NAME}:${DOCKER_IMAGE_TAG} ${DOCKER_IMAGE_NAME}:latest
                '''
            }
        }
        
        stage('Test Docker Image') {
            steps {
                echo 'Testing Docker image...'
                sh '''
                    # Run container in background
                    docker run -d --name test-container -p 8001:8000 ${DOCKER_IMAGE_NAME}:${DOCKER_IMAGE_TAG}
                    
                    # Wait for container to start
                    sleep 10
                    
                    # Test health endpoint
                    curl -f http://localhost:8001/ || exit 1
                    
                    # Stop and remove test container
                    docker stop test-container
                    docker rm test-container
                '''
            }
        }
        
        stage('Push to Docker Hub') {
            when {
                branch 'main'
            }
            steps {
                echo 'Pushing Docker image to Docker Hub...'
                sh '''
                    echo $DOCKER_HUB_CREDENTIALS_PSW | docker login -u $DOCKER_HUB_CREDENTIALS_USR --password-stdin
                    docker push ${DOCKER_IMAGE_NAME}:${DOCKER_IMAGE_TAG}
                    docker push ${DOCKER_IMAGE_NAME}:latest
                    docker logout
                '''
            }
        }
        
        stage('Deploy to Test Environment') {
            when {
                branch 'main'
            }
            steps {
                echo 'Deploying to test environment...'
                sh '''
                    # Stop existing container if running
                    docker stop waste-monitor-test || true
                    docker rm waste-monitor-test || true
                    
                    # Run new container
                    docker run -d \
                        --name waste-monitor-test \
                        -p 8080:8000 \
                        --restart unless-stopped \
                        ${DOCKER_IMAGE_NAME}:latest
                    
                    echo "Application deployed and running on port 8080"
                '''
            }
        }
    }
    
    post {
        always {
            script {
                echo 'Cleaning up...'
                sh '''
                    rm -rf venv || true
                    docker image prune -f || true
                '''
            }
        }
        
        success {
            echo 'Pipeline completed successfully!'
            emailext(
                subject: "Jenkins Build ${BUILD_NUMBER} - SUCCESS",
                body: "The build completed successfully. Check console output at ${BUILD_URL}",
                to: "team@example.com"
            )
        }
        
        failure {
            echo 'Pipeline failed!'
            emailext(
                subject: "Jenkins Build ${BUILD_NUMBER} - FAILURE",
                body: "The build failed. Check console output at ${BUILD_URL}",
                to: "team@example.com"
            )
        }
    }
}
