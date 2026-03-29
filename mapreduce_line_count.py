import sys
from pyspark import SparkContext

if __name__ == "__main__":
    sc = SparkContext(appName="RepoLineCount")
    
    input_path = sys.argv[1]

    files_rdd = sc.wholeTextFiles(input_path)
    
    def count_lines(record):
        filepath, content = record
        filename = filepath.split("/")[-1]
        line_count = len(content.splitlines())
        return f'"{filename}": {line_count}'

    results = files_rdd.map(count_lines).collect()
    
    print("\n" + "="*60)
    print("🚀 HADOOP MAPREDUCE RESULTS:")
    print("="*60)
    for res in results:
        print(res)
    print("="*60 + "\n")
    
    sc.stop()
