#!/usr/bin/env python3

import os
import sys
import struct
import time


class Block:

	def __init__(self, previous_hash="00000000000000000000000000000000", timestamp=0.0, case_id="0000000000000000",
				 evidence_id=0, state="INITIAL", data_length=14, data="Initial block"):
		self.previous_hash = previous_hash
		self.timestamp = timestamp
		self.case_id = case_id
		self.evidence_id = evidence_id
		self.state = state
		self.data_length = data_length
		self.data = data

	def __str__(self):
		return 'Previous Hash: {}\nTimestamp: {}\nCase ID: {}\nEvidence ID: {}\nState: {}\nData Length: {}\nData: {}'.format(
			self.previous_hash, self.timestamp, self.case_id, self.evidence_id, self.state, self.data_length, self.data)


def load_file():
	working_dir = os.getcwd()
	env_path = os.environ.get("BCHOC_FILE_PATH")

	if env_path is not None:
		filepath_to_chain = os.path.join(working_dir, env_path)
	else:
		filepath_to_chain = "bchoc_data"

		if not os.path.isfile(filepath_to_chain):
			with open(filepath_to_chain, 'w'):
				print("file created")
				pass

	return filepath_to_chain


def init():
	filepath = load_file()

	if os.stat(filepath).st_size == 0:

		# If file is empty, init block is created and written to file
		init_block = Block()
		init_bytes = pack_bytes(init_block, 14)

		with open(filepath, 'wb') as f:
			f.write(init_bytes)

	else:

		blockchain = parse_file(filepath)


# check whether init block unpacks correctly
# if not, build init block

def parse_file(filepath):
	blockchain = []

	# unpacks init block
	with open(filepath, 'rb') as f:
		info = f.read(90)
		unpacked = struct.unpack('32s d 16s I 12s I 14s', info)

		init_block = Block(unpacked[0].decode("utf-8").rstrip('\x00'), unpacked[1], unpacked[2].decode("utf-8").rstrip('\x00'), unpacked[3],
						   unpacked[4].decode("utf-8").rstrip('\x00'), unpacked[5], unpacked[6].decode("utf-8").rstrip('\x00'))

		blockchain.append(init_block)

		# this works for checking following blocks, make it less ugly
		while f.peek(76):
			lookahead = f.peek(76)
			next_data_length = lookahead[72:76]
			next_data_length = struct.unpack('I', next_data_length)[0]
			print("the length is: " + str(next_data_length))

			lookahead = f.read(76+next_data_length)
			unpacked = struct.unpack(f'32s d 16s I 12s I {next_data_length}s', lookahead)
			new_block = Block(unpacked[0].decode("utf-8").rstrip('\x00'), unpacked[1], unpacked[2].decode("utf-8").rstrip('\x00'), unpacked[3],
						   unpacked[4].decode("utf-8").rstrip('\x00'), unpacked[5], unpacked[6].decode("utf-8").rstrip('\x00'))

			blockchain.append(new_block)

		return blockchain


def pack_bytes(cur, data_length):
	return_bytes = struct.pack(f'32s d 16s I 12s I {data_length}s', bytes(cur.previous_hash, 'utf-8'), cur.timestamp,
							   bytes(cur.case_id, 'utf-8'), cur.evidence_id, bytes(cur.state, 'utf-8'), cur.data_length,
							   bytes(cur.data, 'utf-8'))
	return return_bytes


def build_from_file():
	pass


def handle_input():
	pass


def main():
	init()


if __name__ == "__main__":
	main()

# print(round(time.time(), 6))
#
# with open(filepath_to_chain, 'rb') as f:
#     info = f.read(90)
#     unpacked = struct.unpack('32s d 16s I 12s I 14s', info)
#     print(unpacked)
#
#     # use this for every block following the init but:
#     # instead of removing 14s, do a f.peak(72) and unpack those bytes to get length
#     # then add the num to the unpack with {} if its greater than 0
#
#     info = f.read(76)
#     unpacked = struct.unpack('32s d 16s I 12s I', info)
#     print(unpacked)
