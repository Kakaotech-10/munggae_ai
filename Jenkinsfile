pipeline {
    agent any

    environment {
        DOCKER_CREDENTIALS_ID = 'dockerhub-credentials'
        AI_IMAGE_REPO = "ella00/munggae-ai" 
    }
    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        
        stage('Build and Push Docker Image') {
            when {
                branch 'main'
            }
            steps {
                script {
                    withCredentials([usernamePassword(credentialsId: DOCKER_CREDENTIALS_ID, usernameVariable: 'DOCKER_USERNAME', passwordVariable: 'DOCKER_PASSWORD')]) {
                        script {
                            def imageTag = "${env.BUILD_NUMBER}"
                            sh 'ls build/libs'
                            sh "docker login -u $DOCKER_USERNAME -p $DOCKER_PASSWORD"
                            sh "docker build -t ${AI_IMAGE_REPO}:${imageTag} -f Dockerfile ."
                            sh "docker push ${AI_IMAGE_REPO}:${imageTag}"
                        }
                    }
                }
            }
        }
    }
    post {
        success {
            echo 'Docker Image build and push succeeded.'
        }
        failure {
            echo 'Build or push failed.'
        }
    }
}
