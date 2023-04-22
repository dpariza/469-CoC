#!/usr/bin/env python3

import os
import sys

env_path = os.environ.get("BCHOH_FILE_PATH")

if env_path is None:
    filepath_to_chain = "bchoh_data"
else:
    filepath_to_chain = env_path

print(filepath_to_chain)

num_args = len(sys.argv)

if num_args <= 1:
    print("Error: must provide args at command line")
    exit(1)
else:
    command = sys.argv[1]
    print(command)
