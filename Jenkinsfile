pipeline {
    agent any

    environment {
        IMAGE_NAME = 'sentiment-ai'
        REGISTRY = 'ghcr.io/aaronba2'
        IMAGE_TAG = "${env.BUILD_NUMBER}"
    }

    stages {

        stage('Checkout') {
            steps {
                checkout scm
                sh 'git log --oneline -5'
            }
        }

        stage('Lint') {
            steps {
                sh '''
                 pip install flake8
                 flake8 src --max-line-length=100
                  '''
            }
        }

        stage('Build & Test') {
            steps {
                sh "docker build -t ${IMAGE_NAME}:${IMAGE_TAG} ."

                sh """
                docker run --rm \
                ${IMAGE_NAME}:${IMAGE_TAG} \
                pytest tests -v \
                --cov=src \
                --cov-report=xml:coverage.xml \
                --cov-report=term-missing \
                --cov-fail-under=70
                """
            }
        }

        stage('Push') {
            when {
                branch 'main'
            }

            steps {
                withCredentials([
                    usernamePassword(
                        credentialsId: 'github-token',
                        usernameVariable: 'REGISTRY_USER',
                        passwordVariable: 'REGISTRY_PASS'
                    )
                ]) {

                    sh '''
                    echo $REGISTRY_PASS | docker login ghcr.io -u $REGISTRY_USER --password-stdin

                    docker tag sentiment-ai:${IMAGE_TAG} ghcr.io/aaronba2/sentiment-ai:${IMAGE_TAG}
                    docker push ghcr.io/aaronba2/sentiment-ai:${IMAGE_TAG}

                    docker tag sentiment-ai:${IMAGE_TAG} ghcr.io/aaronba2/sentiment-ai:latest
                    docker push ghcr.io/aaronba2/sentiment-ai:latest
                    '''
                }
            }
        }
    }

    post {
        always {
            sh 'docker compose down -v || true'
        }
    }
}