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
                        REPO_URL="https://github.com/haotiany-cmu-F25/mayavi.git"

                        echo "Creating bucket (if not exists)..."
                        gcloud storage buckets create gs://$BUCKET_NAME --project=$PROJECT_ID --location=$REGION || true

                        echo "Step 1: Cloning target repository..."
                        rm -rf /tmp/mayavi_repo
                        git clone --depth 1 "$REPO_URL" /tmp/mayavi_repo
                        rm -rf /tmp/mayavi_repo/.git

                        echo "Step 2: Pre-processing files into input.txt..."
                        cd /tmp/mayavi_repo
                        > /tmp/input.txt
                        find . -type f | while IFS= read -r filepath; do
                            relpath="${filepath#./}"
                            while IFS= read -r line || [ -n "$line" ]; do
                                printf '%s\t%s\n' "$relpath" "$line" >> /tmp/input.txt
                            done < "$filepath" 2>/dev/null || true
                        done
                        cd -

                        FILE_COUNT=$(find /tmp/mayavi_repo -type f | wc -l)
                        LINE_COUNT=$(wc -l < /tmp/input.txt)
                        echo "Pre-processed $FILE_COUNT files into $LINE_COUNT lines"

                        echo "Step 3: Uploading input and scripts to GCS..."
                        gsutil cp /tmp/input.txt gs://$BUCKET_NAME/input/input.txt
                        gsutil cp mapper.py gs://$BUCKET_NAME/scripts/mapper.py
                        gsutil cp reducer.py gs://$BUCKET_NAME/scripts/reducer.py

                        echo "Step 4: Cleaning previous output (if any)..."
                        gsutil rm -r gs://$BUCKET_NAME/output/ 2>/dev/null || true

                        echo "Step 5: Submitting Hadoop Streaming job..."
                        gcloud dataproc jobs submit hadoop \
                            --cluster=$CLUSTER_NAME \
                            --region=$REGION \
                            --project=$PROJECT_ID \
                            --jar=file:///usr/lib/hadoop/hadoop-streaming.jar \
                            -- \
                            -input gs://$BUCKET_NAME/input/input.txt \
                            -output gs://$BUCKET_NAME/output \
                            -mapper "python3 mapper.py" \
                            -reducer "python3 reducer.py" \
                            -file gs://$BUCKET_NAME/scripts/mapper.py \
                            -file gs://$BUCKET_NAME/scripts/reducer.py

                        echo "===== HADOOP STREAMING JOB COMPLETE ====="

                        echo "Step 6: Downloading results..."
                        echo "============================================================" > hadoop_results.txt
                        echo "HADOOP MAPREDUCE RESULTS:" >> hadoop_results.txt
                        echo "============================================================" >> hadoop_results.txt
                        gsutil cat gs://$BUCKET_NAME/output/part-* >> hadoop_results.txt
                        echo "============================================================" >> hadoop_results.txt
                        echo "Total files: $FILE_COUNT" >> hadoop_results.txt

                        echo "Results saved to hadoop_results.txt"
                        gsutil cp hadoop_results.txt gs://$BUCKET_NAME/hadoop_results.txt
                    '''
                }
            }
            post {
                success {
                    archiveArtifacts artifacts: 'hadoop_results.txt', fingerprint: true
                }
            }
        }

    }
}
