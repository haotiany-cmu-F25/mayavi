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

        stage('Deploy to Hadoop (Dataproc)') {
            steps {
                script {
                    echo "开始部署任务到 Dataproc..."
                    
                    // 1. 临时下载并安装 gcloud 工具 (静默安装)
                    sh '''
                        curl -sSL https://sdk.cloud.google.com | bash > /dev/null
                        export PATH=$PATH:/home/jenkins/google-cloud-sdk/bin
                        
                        # 2. 提交 Pyspark 任务到集群
                        # ⚠️ 请把下面的 YOUR_CLUSTER_NAME 和 YOUR_REGION 换成你真实的数据
                        gcloud dataproc jobs submit pyspark run_analysis.py \
                            --cluster=project1-hadoop-cluster \
                            --region=us-central1
                    '''
                }
            }
        }
    }
}
