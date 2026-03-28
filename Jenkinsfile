pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                // 1. 拉取 GitHub 上的最新代码
                checkout scm
            }
        }
        
        stage('SonarQube Analysis') {
            steps {
                // 2. 调用我们在 Terraform 里配置好的 SonarQube 服务器进行分析
                // 'my-sonarqube-server' 必须和我们在 JCasC 里定义的名字完全一致
                withSonarQubeEnv('project1-sonarqube-server') {
                    // 运行 Sonar 扫描器，并将结果推送到 SonarQube 平台
                    sh 'sonar-scanner -Dsonar.projectKey=mayavi-project -Dsonar.sources=.'
                }
            }
        }
    }
}
