pipeline {
    agent any

    environment {
        IMAGE_NAME = 'sentiment-ai'
        REGISTRY = 'ghcr.io/aaronba2'
    }

    stages {

        stage('Checkout') {
            steps {

                checkout scm

                script {
                    env.IMAGE_TAG = sh(
                        script: 'git rev-parse --short HEAD',
                        returnStdout: true
                    ).trim()
                }

                echo "Commit : ${env.GIT_COMMIT}"
                echo "Image Tag : ${env.IMAGE_TAG}"

                sh 'git log --oneline -5'
            }
        }

        stage('Lint') {
            steps {

                sh '''
                docker run --rm \
                --volumes-from jenkins \
                -w $WORKSPACE \
                python:3.11-slim \
                sh -c "pip install flake8 -q && flake8 src/ --max-line-length=100"
                '''
            }
        }

        stage('IaC Validate') {
            steps {
                dir('infra') {
                    sh 'terraform init -backend=false -input=false'
                    sh 'terraform fmt -check'
                    sh 'terraform validate'
                }
            }
        }

        stage('Build & Test') {
            steps {

                sh """
                docker build -t ${IMAGE_NAME}:${IMAGE_TAG} .

                docker rm -f test-runner 2>/dev/null || true

                set +e

                docker run \
                --name test-runner \
                -e CI=true \
                ${IMAGE_NAME}:${IMAGE_TAG} \
                pytest tests/ -v \
                --cov=src \
                --cov-report=xml:/tmp/coverage.xml \
                --cov-report=term-missing \
                --cov-fail-under=70

                TEST_EXIT_CODE=\$?

                set -e

                docker cp test-runner:/tmp/coverage.xml ./coverage.xml 2>/dev/null || true

                docker rm -f test-runner 2>/dev/null || true

                exit \$TEST_EXIT_CODE
                """
            }

            post {
                failure {
                    echo 'Tests échoués ou couverture insuffisante (<70%)'
                }
            }
        }

        stage('SonarQube Analysis') {

            environment {
                SONARQUBE_TOKEN = credentials('sonar-token')
            }

            steps {

                withSonarQubeEnv('sonarqube') {

                    sh """
                    docker run --rm \
                    --network cicd-network \
                    --volumes-from jenkins \
                    -w \$WORKSPACE \
                    -e SONAR_HOST_URL=\$SONAR_HOST_URL \
                    -e SONAR_TOKEN=\$SONARQUBE_TOKEN \
                    sonarsource/sonar-scanner-cli:latest \
                    sonar-scanner \
                    -Dsonar.projectKey=sentiment-ai \
                    -Dsonar.projectName=SentimentAI \
                    -Dsonar.projectBaseDir=\$WORKSPACE \
                    -Dsonar.sources=src \
                    -Dsonar.python.version=3.11 \
                    -Dsonar.python.coverage.reportPaths=coverage.xml \
                    -Dsonar.sourceEncoding=UTF-8 \
                    -Dsonar.scanner.metadataFilePath=\$WORKSPACE/report-task.txt
                    """
                }
            }
        }

        stage('Quality Gate') {
            steps {
                timeout(time: 15, unit: 'MINUTES') {
                    waitForQualityGate abortPipeline: true
                }
            }
        }

        stage('Security Scan') {
            steps {

                sh """
                docker run --rm \
                -v /var/run/docker.sock:/var/run/docker.sock \
                -v trivy-cache:/root/.cache/trivy \
                aquasec/trivy:latest image \
                --severity HIGH,CRITICAL \
                --exit-code 0 \
                --format table \
                ${IMAGE_NAME}:${IMAGE_TAG}
                """
            }

            post {
                failure {
                    echo 'Vulnérabilités CRITICAL ou HIGH détectées !'
                    echo 'Corrigez les dépendances avant de déployer.'
                }
            }
        }

        stage('Push') {
            steps {

                withCredentials([
                    usernamePassword(
                        credentialsId: 'github-token',
                        usernameVariable: 'REGISTRY_USER',
                        passwordVariable: 'REGISTRY_PASS'
                    )
                ]) {

                    sh """
                    echo \$REGISTRY_PASS | docker login ghcr.io -u \$REGISTRY_USER --password-stdin

                    docker tag ${IMAGE_NAME}:${IMAGE_TAG} ${REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}

                    docker push ${REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}

                    docker tag ${REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG} ${REGISTRY}/${IMAGE_NAME}:latest

                    docker push ${REGISTRY}/${IMAGE_NAME}:latest
                    """
                }
            }
        }

        stage('IaC Apply') {

            steps {
                dir('infra') {

                    sh 'terraform init -input=false'

                    sh """
                    DOCKER_HOST=unix:///var/run/docker.sock \
                    terraform apply -auto-approve \
                    -var="image_tag=${IMAGE_TAG}"
                    """
                }
            }
        }

        stage('Deploy Staging') {

            steps {

                echo "Attente du healthcheck du conteneur..."

                sh '''
                timeout 60 sh -c '
                until [ "$(docker inspect sentiment-staging --format="{{.State.Health.Status}}")" = "healthy" ];
                do
                    echo "Waiting for container healthcheck..."
                    sleep 5
                done
                '

                docker inspect sentiment-staging --format="{{.State.Health.Status}}"
                '''
            }
        }

        stage('Smoke Test') {

            steps {

                sh '''
                echo "Attente démarrage..."
                sleep 10

                curl -f http://localhost:8001/health
                echo "/health OK"

                curl -s http://localhost:8001/metrics | \
                grep sentiment_predictions_total
                echo "/metrics OK"

                sleep 20

                curl -f http://localhost:9090/-/healthy
                echo "Prometheus OK"

                curl -f http://localhost:3000/api/health
                echo "Grafana OK"
                '''
            }
        }
    }

    post {

        success {
            echo 'Pipeline réussi !'
            echo "Image : ${REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}"
        }

        failure {
            echo 'Pipeline échoué.'
        }
    }
}
