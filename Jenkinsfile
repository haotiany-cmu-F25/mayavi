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
                            sh 'sonar-scanner -Dsonar.projectKey=mayavi-project -Dsonar.sources=.'
                        }
                    }
                }
            }
        }

        // 👇 新增：拦路虎阶段（自动等待 SonarQube 的裁判结果）
        stage('Quality Gate') {
            steps {
                // 等待 SonarQube 返回结果（最多等 10 分钟）
                timeout(time: 10, unit: 'MINUTES') {
                    // 如果门禁没过（比如有 Blocker），直接中止流水线！
                    waitForQualityGate abortPipeline: true
                }
                echo "🎉 代码质量完美，没有 Blocker！准备向 Hadoop 进发！"
            }
        }

        // 👇 新增：Hadoop 部署阶段的占位符
        stage('Deploy to Hadoop (Dataproc)') {
            steps {
                echo "这里将执行 gcloud dataproc jobs submit 命令..."
            }
        }
    }
}
