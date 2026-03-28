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
                    // 1. 核心修复：呼叫我们在 Terraform JCasC 里配置的名为 "sonar-scanner" 的工具
                    def scannerHome = tool 'sonar-scanner'
                    
                    // 2. 将下载好的工具路径临时加入到 Jenkins 运行环境的 PATH 里
                    withEnv(["PATH+SONAR=${scannerHome}/bin"]) {
                        
                        // 3. 登录 SonarQube 服务器
                        withSonarQubeEnv('project1-sonarqube-server') {
                            
                            // 4. 执行代码扫描
                            sh 'sonar-scanner -Dsonar.projectKey=mayavi-project -Dsonar.sources=.'
                        }
                    }
                }
            }
        }
    }
}
