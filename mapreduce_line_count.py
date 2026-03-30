import os
import sys
import subprocess
import tempfile
import shutil
from pyspark import SparkContext

if __name__ == "__main__":
    # Suppress verbose Spark/Hadoop INFO logs
    import logging
    logging.getLogger("py4j").setLevel(logging.WARN)
    repo_url = (
        sys.argv[1]
        if len(sys.argv) > 1
        else "https://github.com/haotiany-cmu-F25/mayavi.git"
    )
    output_bucket = (
        sys.argv[2]
        if len(sys.argv) > 2
        else "gs://cmu-cloud-infra-485621-hadoop-repo-data"
    )

    # Step 1: Clone repo on the driver node
    clone_dir = tempfile.mkdtemp(prefix="mayavi_repo_")
    print(">>> Step 1: Cloning repository...")
    subprocess.run(["git", "clone", "--depth", "1", repo_url, clone_dir], check=True)
    shutil.rmtree(os.path.join(clone_dir, ".git"), ignore_errors=True)
    print(">>> Clone complete.")

    # Step 2: Count lines locally and collect (filename, line_count) pairs
    print(">>> Step 2: Counting lines in all files...")
    file_data = []
    for root, dirs, files in os.walk(clone_dir):
        for fname in files:
            fpath = os.path.join(root, fname)
            rel_path = os.path.relpath(fpath, clone_dir)
            try:
                with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
                    line_count = sum(1 for _ in f)
                file_data.append((rel_path, line_count))
            except Exception:
                file_data.append((rel_path, 0))

    print(">>> Found {0} files.".format(len(file_data)))

    # Step 3: Use Spark to distribute and process the data (MapReduce)
    print(">>> Step 3: Running Spark MapReduce job...")
    sc = SparkContext(appName="RepoLineCount")
    sc.setLogLevel("WARN")

    # Distribute file data across the 3 worker nodes
    rdd = sc.parallelize(file_data, numSlices=min(len(file_data), 30))

    # MAP: format each record as the required output
    formatted_rdd = rdd.map(lambda x: '"{0}": {1}'.format(x[0], x[1]))

    # REDUCE: sort and collect
    results = formatted_rdd.sortBy(lambda x: x).collect()

    # Build output
    output_lines = []
    output_lines.append("=" * 60)
    output_lines.append("HADOOP MAPREDUCE RESULTS:")
    output_lines.append("=" * 60)
    for res in results:
        output_lines.append(res)
    output_lines.append("=" * 60)
    output_lines.append("Total files: {0}".format(len(results)))

    output_text = "\n".join(output_lines)

    # Save results to GCS (predefined location)
    result_file = "/tmp/hadoop_results.txt"
    with open(result_file, "w") as f:
        f.write(output_text + "\n")

    gcs_output = output_bucket + "/hadoop_results.txt"
    subprocess.run(["gsutil", "cp", result_file, gcs_output], check=True)
    print(">>> Total files processed: {0}".format(len(results)))
    print(">>> Results saved to: " + gcs_output)
    print(
        ">>> View results at: https://console.cloud.google.com/storage/browser/"
        + output_bucket.replace("gs://", "")
    )

    sc.stop()
