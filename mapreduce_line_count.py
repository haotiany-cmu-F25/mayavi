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

    # Collect all file relative paths for later
    file_list = []
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
            file_list.append(rel_path)

    # Step 3: Use Spark to count lines distributed across workers
    # Each file path becomes a task — workers read from HDFS independently
    sc = SparkContext(appName="RepoLineCount")

    hdfs_base = hdfs_path
    paths_rdd = sc.parallelize(file_list, numSlices=max(len(file_list) // 10, 3))

    def count_lines_for_file(rel_path):
        """Each worker reads one file from HDFS and counts its lines."""
        import subprocess as sp
        try:
            result = sp.run(
                ["hdfs", "dfs", "-cat", hdfs_base + "/" + rel_path],
                capture_output=True, text=True, timeout=30
            )
            line_count = len(result.stdout.splitlines())
        except Exception:
            line_count = 0
        return '"{0}": {1}'.format(rel_path, line_count)

    results = paths_rdd.map(count_lines_for_file).collect()

    print("\n" + "=" * 60)
    print("HADOOP MAPREDUCE RESULTS:")
    print("=" * 60)
    for res in sorted(results):
        print(res)
    print("=" * 60 + "\n")

    sc.stop()

    sc.stop()

    sc.stop()
