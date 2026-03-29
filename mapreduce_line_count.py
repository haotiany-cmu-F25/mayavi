import os
import sys
import subprocess
import tempfile
from pyspark import SparkContext

if __name__ == "__main__":
    repo_url = (
        sys.argv[1]
        if len(sys.argv) > 1
        else "https://github.com/haotiany-cmu-F25/mayavi.git"
    )

    # Step 1: Clone the repo on the driver node
    clone_dir = tempfile.mkdtemp(prefix="mayavi_repo_")
    subprocess.run(["git", "clone", "--depth", "1", repo_url, clone_dir], check=True)

    # Step 2: Upload repo files to HDFS so Hadoop can distribute them across nodes
    hdfs_path = "hdfs:///tmp/mayavi_repo"
    subprocess.run(["hdfs", "dfs", "-rm", "-r", "-f", hdfs_path])
    subprocess.run(["hdfs", "dfs", "-mkdir", "-p", hdfs_path])

    for root, dirs, files in os.walk(clone_dir):
        dirs[:] = [d for d in dirs if d != ".git"]
        for fname in files:
            fpath = os.path.join(root, fname)
            rel_path = os.path.relpath(fpath, clone_dir)
            hdfs_dest = hdfs_path + "/" + rel_path
            hdfs_parent = os.path.dirname(hdfs_dest)
            subprocess.run(
                ["hdfs", "dfs", "-mkdir", "-p", hdfs_parent], capture_output=True
            )
            subprocess.run(
                ["hdfs", "dfs", "-put", fpath, hdfs_dest], capture_output=True
            )

    # Step 3: Use Spark to read from HDFS (distributed across 3 workers)
    sc = SparkContext(appName="RepoLineCount")

    files_rdd = sc.wholeTextFiles(hdfs_path + "/*")

    def count_lines(record):
        filepath, content = record
        # Extract relative path from HDFS URI
        rel = (
            filepath.split("/tmp/mayavi_repo/")[-1]
            if "/tmp/mayavi_repo/" in filepath
            else filepath
        )
        line_count = len(content.splitlines())
        return '"{0}": {1}'.format(rel, line_count)

    results = files_rdd.map(count_lines).collect()

    print("\n" + "=" * 60)
    print("HADOOP MAPREDUCE RESULTS:")
    print("=" * 60)
    for res in sorted(results):
        print(res)
    print("=" * 60 + "\n")

    sc.stop()

    sc.stop()
