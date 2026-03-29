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
                echo "🎉 The code quality is perfect, no Blocker! Get ready for Hadoop!"
            }
        }

        stage('Deploy to Hadoop (Dataproc)') {
            steps {
                script {
                    
                    sh '''
                        # ==========================================
                        # 1. 修复并安装 gcloud 工具
                        # ==========================================
                        export CLOUDSDK_PYTHON=python3
                        
                        echo "Installing Google Cloud SDK..."
                        curl -sSL https://sdk.cloud.google.com | bash -s -- --disable-prompts > /dev/null
                        export PATH=$PATH:/home/jenkins/google-cloud-sdk/bin
                        
                        # ==========================================
                        # 2. 配置你的 GCP 参数 (🚨 记得修改这里！！！)
                        # ==========================================
                        PROJECT_ID="cmu-cloud-infra-485621"
                        REGION="us-central1"
                        CLUSTER_NAME="project1-hadoop-cluster"
                        
                        BUCKET_NAME="${PROJECT_ID}-hadoop-repo-data"
                        
                        # ==========================================
                        # 3. 把代码上传到 GCS 存储桶给 Hadoop 读
                        # ==========================================
                        echo "Creating GCS bucket and uploading files..."
                        gcloud storage buckets create gs://$BUCKET_NAME --project=$PROJECT_ID --location=$REGION || true
                        
                        # 同步当前所有文件到 GCS
                        gsutil -m rsync -r -x '\\.git/.*' . gs://$BUCKET_NAME/repo_files/
                        
                        # ==========================================
                        # 4. 直接提交仓库根目录的脚本给 Dataproc
                        # ==========================================
                        echo "Submitting MapReduce job to Dataproc Cluster: $CLUSTER_NAME..."
                        
                        # 直接调用当前目录下的 mapreduce_line_count.py
                        gcloud dataproc jobs submit pyspark mapreduce_line_count.py \
                            --cluster=$CLUSTER_NAME \
                            --region=$REGION \
                            --project=$PROJECT_ID \
                            -- gs://$BUCKET_NAME/repo_files
                    '''
                }
            }
    }
}
