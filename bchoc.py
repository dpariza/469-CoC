#!/usr/bin/env python3

import os
import sys
import struct
import hashlib
import time
import argtest


class Block:

	def __init__(self, previous_hash="ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad", timestamp=0.0,
				 case_id="5ed4bad2e2d111edb5ea0242ac120002", evidence_id=0, state="INITIAL", data_length=14,
				 data="Initial block"):
		self.previous_hash = previous_hash
		self.timestamp = timestamp
		self.case_id = case_id
		self.evidence_id = evidence_id
		self.state = state
		self.data_length = data_length
		self.data = data
		self.new_item = False

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
		init_bytes = pack_bytes(init_block)

		with open(filepath, 'wb') as f:
			f.write(init_bytes)

		print("Blockchain file not found. Created INITIAL block.")

	else:

		blockchain = parse_file(filepath)
		print("Blockchain file found with INITIAL block.")
		for block in blockchain:
			print(block)
		return blockchain


def parse_file(filepath):
	blockchain = []

	# unpacks init block
	with open(filepath, 'rb') as f:
		info = f.read(90)

		# unpacks init block, data length preset as 14
		blockchain.append(unpack_bytes(info, 14))

		# this works for checking following blocks, make it less ugly
		while continues := f.peek(76):
			next_data_length = continues[72:76]
			next_data_length = struct.unpack('I', next_data_length)[0]
			print("the length is: " + str(next_data_length))

			lookahead = f.read(76 + next_data_length)

			blockchain.append(unpack_bytes(lookahead, next_data_length))

		return blockchain


def unpack_bytes(unpack_this, data_length):
	unpacked = struct.unpack(f'32s d 16s I 12s I {data_length}s', unpack_this)

	hash_unpacked = str(hex(int.from_bytes(unpacked[0], "little")))
	hash_unpacked = hash_unpacked[2:]

	case_unpacked = str(hex(int.from_bytes(unpacked[2], "little")))
	case_unpacked = case_unpacked[2:]

	return_block = Block(hash_unpacked, unpacked[1],
						 case_unpacked, unpacked[3],
						 unpacked[4].decode("utf-8").rstrip('\x00'), unpacked[5],
						 unpacked[6].decode("utf-8").rstrip('\x00'))

	return return_block


def write_file(blockchain):
	filepath = load_file()

	with open(filepath, 'ab') as f:
		for block in blockchain:
			if block.new_item:
				write_bytes = pack_bytes(block)
				f.write(write_bytes)


def pack_bytes(cur):
	hash_as_int = int(cur.previous_hash, 16)
	hash_as_int = hash_as_int.to_bytes(32, "little")
	case_as_int = int(cur.case_id, 16)
	case_as_int = case_as_int.to_bytes(16, "little")

	return_bytes = struct.pack(f'32s d 16s I 12s I {cur.data_length}s', hash_as_int,
							   cur.timestamp, case_as_int, cur.evidence_id, bytes(cur.state, 'utf-8'),
							   cur.data_length, bytes(cur.data, 'utf-8'))
	return return_bytes


def add(args):
	pass

def handle_input():
	args = argtest.process_commands()

	if args.command == "add":
		# ex: bchoc add -c case_id -i item_id [-i item_id ...]
		# print("added!")
		add(args)
		pass

	elif args.command == "checkout":
		pass

	elif args.command == "checkin":
		pass

	elif args.command == "log":
		print("log")

		if args.reverse and args.num_entries:
			# ex: bchoc log -r -n 5 -c 66 -i 2
			print(f'Reverse order of {args.num_entries} entries')
		# code here for reverse order of num_entries

		elif args.reverse and not args.num_entries:
			# ex: bchoc log -r -c 66 -i 2
			print('Reverse order of all entries')
		# code here for reverse order of all entries

		elif not args.reverse and args.num_entries:
			# ex: bchoc log -n 5 -c 66 -i 2
			print(f'First {args.num_entries} entries')
		# code here for first num_entries

		else:
			# ex: bchoc log -c 66 -i 2
			# neither reverse and all entries
			print()

	elif args.command == "remove":
		print("remove")

		if args.owner:
			# ex: bchoc remove -i 6 -y idk -o Chris
			print()
		else:
			# ex: bchoc remove -i 6 -y idk
			print()

	elif args.command == "init":
		print()

	elif args.command == "verify":
		print()

	else:
		print(f"Unknown command: {args.command}")
		sys.exit(1)


def main():
	handle_input()
	chain = init()
	#write_file(chain)


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
