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

        stage('Build & Test') {
            steps {

                sh """
                docker build -t ${IMAGE_NAME}:${IMAGE_TAG} .
                """

                sh """
                docker run --rm \
                ${IMAGE_NAME}:${IMAGE_TAG} \
                pytest tests/ -v \
                --cov=src \
                --cov-report=xml:coverage.xml \
                --cov-report=term-missing \
                --cov-fail-under=70
                """
            }

            post {
                failure {
                    echo 'Tests échoués ou couverture insuffisante'
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
                    echo \$REGISTRY_PASS | docker login ghcr.io \
                    -u \$REGISTRY_USER --password-stdin

                    docker tag ${IMAGE_NAME}:${IMAGE_TAG} \
                    ${REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}

                    docker push \
                    ${REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}

                    docker tag \
                    ${REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG} \
                    ${REGISTRY}/${IMAGE_NAME}:latest

                    docker push \
                    ${REGISTRY}/${IMAGE_NAME}:latest
                    """
                }
            }
        }
    }

    post {

        always {
            sh 'docker compose down -v 2>/dev/null || true'
        }

        success {
            echo "Pipeline réussi !"
            echo "Image : ${REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}"
        }

        failure {
            echo 'Pipeline échoué. Consultez les logs.'
        }
    }
}