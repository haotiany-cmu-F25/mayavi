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
                        # 1. 下载自带 Python 环境的完整版 gcloud
                        # ==========================================
                        echo "Downloading Google Cloud SDK (bundled with Python)..."
                        # 直接下载官方的 Linux 64位完整压缩包
                        curl -O https://dl.google.com/dl/cloudsdk/channels/rapid/downloads/google-cloud-cli-linux-x86_64.tar.gz
                        
                        echo "Extracting archive..."
                        tar -xzf google-cloud-cli-linux-x86_64.tar.gz
                        
                        # 关键魔法：把解压出来的路径临时加到系统的 PATH 里
                        export PATH=$PWD/google-cloud-sdk/bin:$PATH
                        # 强制 gcloud 使用它自己肚子里自带的 Python，彻底摆脱对 Jenkins 系统的依赖！
                        export CLOUDSDK_PYTHON=$PWD/google-cloud-sdk/platform/bundledpythonunix/bin/python3
                        
                        # 打印一下版本，证明安装成功
                        gcloud --version
                        
                        # ==========================================
                        # 2. 配置你的 GCP 参数 (已保留你真实数据)
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
                        
                        gsutil -m rsync -r -x '\\.git/.*' . gs://$BUCKET_NAME/repo_files/
                        
                        # ==========================================
                        # 4. 直接提交仓库根目录的脚本给 Dataproc
                        # ==========================================
                        echo "Submitting MapReduce job to Dataproc Cluster: $CLUSTER_NAME..."
                        
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
}
