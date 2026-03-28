pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        
        stage('SonarQube Analysis') {
            steps {
                script {
                    def scannerHome = tool 'sonar-scanner'
                    
                    withEnv(["PATH+SONAR=${scannerHome}/bin"]) {
                        
                        withSonarQubeEnv('project1-sonarqube-server') {
                            
                            sh "sonar-scanner -Dsonar.projectKey=mayavi-project -Dsonar.sources=. -Dsonar.token=\${SONAR_AUTH_TOKEN}"
                        }
                    }
                }
            }
        }
    }
}
