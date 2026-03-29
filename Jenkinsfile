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

        stage('Quality Gate') {
            steps {
                timeout(time: 10, unit: 'MINUTES') {
                    waitForQualityGate abortPipeline: true
                }
                echo "🎉 The code quality is perfect, no Blocker! Get ready for Hadoop!"
            }
        }

        stage('Deploy to Hadoop (Dataproc)') {
            steps {
                script {
                    sh '''
                        echo "Downloading Google Cloud SDK..."
                        curl -O https://dl.google.com/dl/cloudsdk/channels/rapid/downloads/google-cloud-cli-linux-x86_64.tar.gz
                        tar -xzf google-cloud-cli-linux-x86_64.tar.gz

                        export PATH=$PWD/google-cloud-sdk/bin:$PATH
                        export CLOUDSDK_PYTHON=$PWD/google-cloud-sdk/platform/bundledpythonunix/bin/python3

                        gcloud --version

                        PROJECT_ID="cmu-cloud-infra-485621"
                        REGION="us-central1"
                        CLUSTER_NAME="project1-hadoop-cluster"
                        BUCKET_NAME="${PROJECT_ID}-hadoop-repo-data"

                        echo "Creating bucket (if not exists)..."
                        gcloud storage buckets create gs://$BUCKET_NAME --project=$PROJECT_ID --location=$REGION || true

                        echo "Uploading PySpark script..."
                        gsutil cp mapreduce_line_count.py gs://$BUCKET_NAME/mapreduce_line_count.py

                        echo "Submitting Hadoop job..."
                        gcloud dataproc jobs submit pyspark gs://$BUCKET_NAME/mapreduce_line_count.py \
                            --cluster=$CLUSTER_NAME \
                            --region=$REGION \
                            --project=$PROJECT_ID \
                            -- https://github.com/haotiany-cmu-F25/mayavi.git gs://$BUCKET_NAME

                        echo "Results saved to: gs://$BUCKET_NAME/hadoop_results.txt"
                        echo "===== HADOOP RESULTS ====="
                        gsutil cat gs://$BUCKET_NAME/hadoop_results.txt
                    '''
                }
            }
        }

    }
}
