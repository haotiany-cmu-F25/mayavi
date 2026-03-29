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

                        echo "Uploading to GCS..."
                        gcloud storage buckets create gs://$BUCKET_NAME --project=$PROJECT_ID --location=$REGION || true
                        gsutil -m rsync -r -x '\\.git/.*' . gs://$BUCKET_NAME/repo_files/

                        echo "Submitting job..."
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
