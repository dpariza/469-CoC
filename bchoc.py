#!/usr/bin/env python3

import sys

num_args = len(sys.argv)

if num_args <= 1:
    print("Error: must provide args at command line")
    exit(1)
else:
    command = sys.argv[1]
    print(command)



