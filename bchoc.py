#!/usr/bin/env python3

import os
import sys
import struct
import uuid

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

    if sys.argv[1] = "init": # handle init
        # check first for if there are any blocks on the bchoc_data
        # if no blocks, then create one

        # if file exit with a blockchain already in it then just print
        # print("Blockhain file found with INITIAL block.")

        # else initialize the blockchain file and INITIAL block.
        # when initializing we can use this
        # initblock = struct.pack('32s d 16s I 12s I 14s', "00000000000000000000000000000000", TIME, "0000000000000000", 0, "INITIAL", 14, "Initial block")
        # then we can just write out to the file the initblock

    elif sys.argv[1] = "verify": # handle verification
        

    elif sys.argv[1] = "remove": # handle remove
        

    elif sys.argv[1] = "log": # handle log
        

    elif sys.argv[1] = "checkin": # handle checkin
        

    elif sys.argv[1] = "checkout": # handle checkout
        

    elif sys.argv[1] = "add": # handle adding
        
