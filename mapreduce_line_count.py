import os
import sys
import subprocess
import tempfile
import shutil
from pyspark import SparkContext

if __name__ == "__main__":
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

    # Step 1: Clone the repo on the driver node
    clone_dir = tempfile.mkdtemp(prefix="mayavi_repo_")
    print("Cloning repository...")
    subprocess.run(["git", "clone", "--depth", "1", repo_url, clone_dir], check=True)

    # Remove .git directory to avoid uploading it
    shutil.rmtree(os.path.join(clone_dir, ".git"), ignore_errors=True)

    # Step 2: Upload entire repo to HDFS in ONE command
    hdfs_path = "/tmp/mayavi_repo"
    print("Uploading to HDFS...")
    subprocess.run(["hdfs", "dfs", "-rm", "-r", "-f", hdfs_path])
    subprocess.run(["hdfs", "dfs", "-put", clone_dir, hdfs_path], check=True)
    print("HDFS upload complete.")

    # Step 3: Use Spark wholeTextFiles to read from HDFS (distributed across 3 workers)
    sc = SparkContext(appName="RepoLineCount")

    # Recursive glob to read all files including subdirectories
    sc._jsc.hadoopConfiguration().set("mapreduce.input.fileinputformat.input.dir.recursive", "true")
    files_rdd = sc.wholeTextFiles("hdfs://" + hdfs_path + "/*/*")

    def count_lines(record):
        filepath, content = record
        # Extract relative path from the HDFS URI
        marker = "/tmp/mayavi_repo/"
        idx = filepath.find(marker)
        if idx >= 0:
            # Skip the first directory (the cloned dir name)
            parts = filepath[idx + len(marker):].split("/", 1)
            rel = parts[1] if len(parts) > 1 else parts[0]
        else:
            rel = filepath.rsplit("/", 1)[-1]
        line_count = len(content.splitlines())
        return '"{0}": {1}'.format(rel, line_count)

    results = files_rdd.map(count_lines).collect()
    results_sorted = sorted(results)

    # Print results
    output_lines = []
    output_lines.append("=" * 60)
    output_lines.append("HADOOP MAPREDUCE RESULTS:")
    output_lines.append("=" * 60)
    for res in results_sorted:
        output_lines.append(res)
    output_lines.append("=" * 60)

    output_text = "\n".join(output_lines)
    print("\n" + output_text + "\n")

    # Save results to a local file, then copy to GCS
    result_file = "/tmp/hadoop_results.txt"
    with open(result_file, "w") as f:
        f.write(output_text + "\n")

    gcs_output = output_bucket + "/hadoop_results.txt"
    subprocess.run(["gsutil", "cp", result_file, gcs_output], check=True)
    print("Results saved to: " + gcs_output)

    sc.stop()

    sc.stop()

    sc.stop()

    sc.stop()
