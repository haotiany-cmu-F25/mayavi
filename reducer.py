#!/usr/bin/env python3
"""Hadoop Streaming Reducer: sum line counts per file.

Input (sorted by Hadoop): filename<TAB>1
Output: "filename": count
"""
import sys

current_file = None
current_count = 0

for line in sys.stdin:
    parts = line.strip().split('\t', 1)
    if len(parts) != 2:
        continue
    filename, val = parts
    try:
        count = int(val)
    except ValueError:
        continue

    if filename == current_file:
        current_count += count
    else:
        if current_file is not None:
            print('"{0}": {1}'.format(current_file, current_count))
        current_file = filename
        current_count = count

if current_file is not None:
    print('"{0}": {1}'.format(current_file, current_count))
