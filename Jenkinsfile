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
                bat 'docker build -t sentiment-ai:jenkins .'
            }
        }

        stage('Tests') {
            steps {
                bat 'docker run --rm sentiment-ai:jenkins pytest tests -v'
            }
        }
    }
}