pipeline {
    agent any

    stages {

        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Build Docker') {
            steps {
                sh 'docker build -t sentiment-ai:jenkins .'
            }
        }

        stage('Tests') {
            steps {
                sh 'docker run --rm sentiment-ai:jenkins pytest tests -v'
            }
        }
    }
}