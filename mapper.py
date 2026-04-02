#!/usr/bin/env python3
"""Hadoop Streaming Mapper: emit (filename, 1) for each line in input.

Input format (pre-processed): filename<TAB>line_content
Output: filename<TAB>1
"""
import sys

for line in sys.stdin:
    parts = line.split('\t', 1)
    if len(parts) >= 1 and parts[0]:
        print("{0}\t1".format(parts[0].strip()))
