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
                        
                        // 只需要填对名字，凭证注入交给 Jenkins 系统处理
                        withSonarQubeEnv('project1-sonarqube-server') {
                            
                            // 🌟 注意这里：不要手动传 -Dsonar.token
                            sh 'sonar-scanner -Dsonar.projectKey=mayavi-project -Dsonar.sources=.'
                        }
                    }
                }
            }
        }
    }
}
