pipeline {
    agent any

    environment {
        DOCKER_CREDENTIALS_ID = 'dockerhub-credentials'
        AI_IMAGE_REPO = "ella00/munggae-ai"
        AI_API_KEY = credentials('ai-api-key')
        AWS_ACCESS_KEY_ID = credentials('aws-access-key-id')
        AWS_SECRET_ACCESS_KEY = credentials('aws-secret-access-key')
        AWS_DEFAULT_REGION = credentials('aws-region')

    }
    stages {
        stage('Checkout and Download model') {
            steps {
                checkout([$class: 'GitSCM', branches: [[name: '*/main']], 
                          extensions: [[$class: 'CleanBeforeCheckout']], 
                          userRemoteConfigs: [[url: 'https://github.com/Kakaotech-10/munggae_ai.git']]])
                echo "Downloading Model from S3..."
                sh """
                    aws s3 cp s3://munggae-ai-kobert/ model/ --recursive
                """
                sh 'ls -lh model/koBERT_model_v1.01/model.safetensors'
            }
        }
        
        stage('Set Environment Variable') {
            steps {
                script {
                    sh 'echo "api_key=${AI_API_KEY}" >> .env'
                    sh 'cd ..'
                    stash includes: '**/*', name: 'munggae_ai'
                }
            }
        }
        
        stage('Build and Push Docker Image') {
            agent { label 'dind-agent' }
            steps {
                script {
                    unstash 'munggae_ai'
                    withCredentials([usernamePassword(credentialsId: DOCKER_CREDENTIALS_ID, usernameVariable: 'DOCKER_USERNAME', passwordVariable: 'DOCKER_PASSWORD')]) {
                        def imageTag = "${env.BUILD_NUMBER}"
                        sh 'ls -lh model/koBERT_model_v1.01/model.safetensors'
                        sh "docker login -u $DOCKER_USERNAME -p $DOCKER_PASSWORD"
                        sh "docker build -t ${AI_IMAGE_REPO}:${imageTag} -f Dockerfile ."
                        sh "docker push ${AI_IMAGE_REPO}:${imageTag}"
                    }
                }
            }
        }
        stage('Checkout Manifest Repository') {
            agent { label 'java-docker' }
            steps {
                script {
                    checkout([$class: 'GitSCM', branches: [[name: '*/main']], 
                              extensions: [[$class: 'CleanBeforeCheckout']], 
                              userRemoteConfigs: [[url: 'https://github.com/Kakaotech-10/munggae-manifest.git']]])
                    withCredentials([usernamePassword(credentialsId: 'github-token', usernameVariable: 'GIT_USERNAME', passwordVariable: 'GIT_PASSWORD')]) {
                        sh """
                        git config --local user.email "als33396dn@gmail.com"
                        git config --local user.name "KimMinWoooo"
                        # Ensure on main branch
                        git checkout -B main origin/main
                        echo "Current directory contents:"
                        ls -la
                        # Navigate to Backend directory if it exists
                        if [ -d "AI" ]; then
                          cd AI
                        else
                          echo "AI directory not found. Listing current directory contents."
                        fi
                        echo "Current directory after navigation:"
                        ls -la
                        # Update image tag in FastAPI-munggae.yaml with the new build number
                        sed -i "s|image: ella00/munggae-ai:.*|image: ella00/munggae-ai:${env.BUILD_NUMBER}|" FastAPI-munggae.yaml
                        # Commit and push the changes
                        git add .
                        git commit -m "Update image tag to ${env.BUILD_NUMBER} for ArgoCD"
                        git push https://${GIT_USERNAME}:${GIT_PASSWORD}@github.com/Kakaotech-10/munggae-manifest.git main
                        """
                    }
                }
            }
        }
    }
    //jenkins 빌드 결과 slack 알림
    post  {
        success {
            slackSend (
                channel: 'jenkins-알람',
                color: '#2C953C',
                message: "AI - SUCCESSFUL: Job ${env.JOB_NAME} #${env.BUILD_NUMBER} (${env.BUILD_URL})"
            )
        }
        failure {
            slackSend (
                channel: 'jenkins-알람',
                color: '#FF3232',
                message: "AI - FAIL: Job ${env.JOB_NAME} #${env.BUILD_NUMBER} (${env.BUILD_URL})"
            )
        }
    }
}
