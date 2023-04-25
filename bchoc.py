#!/usr/bin/env python3

import os
import sys
import struct
import hashlib
import time
import argtest
from datetime import datetime
import uuid
import copy


class Block:

	def __init__(self, previous_hash="0000000000000000000000000000000000000000000000000000000000000000",
				 timestamp=round(time.time(), 6),
				 case_id="00000000000000000000000000000000", evidence_id=0, state="INITIAL", data_length=14,
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
			self.previous_hash, datetime.fromtimestamp(self.timestamp).isoformat() + 'Z', uuid.UUID(self.case_id),
			self.evidence_id, self.state, self.data_length, self.data)


def get_time():
	return round(time.time(), 6)


def load_file():
	working_dir = os.getcwd()
	env_path = os.environ.get("BCHOC_FILE_PATH")

	if env_path is not None:
		filepath_to_chain = os.path.join(working_dir, env_path)
	else:
		filepath_to_chain = "bchoc_data"

		if not os.path.isfile(filepath_to_chain):
			with open(filepath_to_chain, 'w'):
				pass

	return filepath_to_chain


def unpack_bytes(unpack_this, data_length):
	unpacked = struct.unpack(f'32s d 16s I 12s I {data_length}s', unpack_this)

	hash_unpacked = str(hex(int.from_bytes(unpacked[0], "little")))[2:]

	if hash_unpacked == '0':
		hash_unpacked = '0000000000000000000000000000000000000000000000000000000000000000'

	case_unpacked = str(hex(int.from_bytes(unpacked[2], "little")))[2:]

	if case_unpacked == '0':
		case_unpacked = '00000000000000000000000000000000'

	return_block = Block(hash_unpacked, unpacked[1],
						 case_unpacked, unpacked[3],
						 unpacked[4].decode("utf-8").rstrip('\x00'), unpacked[5],
						 unpacked[6].decode("utf-8").rstrip('\x00'))

	return return_block


def pack_bytes(cur):
	hash_as_int = int(cur.previous_hash, 16)
	hash_as_int = hash_as_int.to_bytes(32, "little")
	case_as_int = int(cur.case_id, 16)
	case_as_int = case_as_int.to_bytes(16, "little")

	return_bytes = struct.pack(f'32s d 16s I 12s I {cur.data_length}s', hash_as_int,
							   cur.timestamp, case_as_int, cur.evidence_id, bytes(cur.state, 'utf-8'),
							   cur.data_length, bytes(cur.data, 'utf-8'))
	return return_bytes


def parse_file(filepath):
	chain = []

	# unpacks init block
	with open(filepath, 'rb') as f:
		info = f.read(90)

		# unpacks init block, data length preset as 14
		chain.append(unpack_bytes(info, 14))

		# this works for checking following blocks, make it less ugly
		while continues := f.peek(76):
			next_data_length = continues[72:76]
			next_data_length = struct.unpack('I', next_data_length)[0]

			lookahead = f.read(76 + next_data_length)

			chain.append(unpack_bytes(lookahead, next_data_length))

		return chain


def setup_blockchain():
	filepath = load_file()

	chain = []

	if os.stat(filepath).st_size == 0:

		# If file is empty, init block is created and written to file
		init_block = Block()
		chain.append(init_block)

		init_bytes = pack_bytes(init_block)

		with open(filepath, 'wb') as f:
			f.write(init_bytes)

		# False flag denotes that initial block was created and added to the new file
		return chain, False

	else:

		blockchain = parse_file(filepath)

		# True flag denotes successful load of existing init block
		return blockchain, True


class Blockchain:

	def __init__(self):
		setup = setup_blockchain()
		self.chain = setup[0]
		self.init_flag = setup[1]
		self.error_state = False
		self.error_message = ''
		self.args = argtest.process_commands()

	def write_file(self):
		filepath = load_file()

		with open(filepath, 'ab') as f:
			for block in self.chain:
				if block.new_item:
					write_bytes = pack_bytes(block)
					f.write(write_bytes)

	def init(self):
		if self.init_flag:
			print("Blockchain file found with INITIAL block.")
		else:
			print("Blockchain file not found. Created INITIAL block.")

	def calculate_hash(self):
		prev = self.chain[-1]
		raw_hashing = prev.previous_hash + str(prev.timestamp) + prev.case_id + str(prev.evidence_id) + prev.state + \
					  str(prev.data_length) + prev.data
		raw_hashing = raw_hashing.encode('utf-8')

		prev_hash = hashlib.sha256(raw_hashing).digest()
		prev_hash = str(hex(int.from_bytes(prev_hash, "little")))

		return prev_hash

	def new_block(self, block_to_add):
		# do all the checks for appending the chain here!
		block_to_add.new_item = True
		self.chain.append(block_to_add)

	def add(self, case_id, evidence_id):

		block_to_add = Block(self.calculate_hash(), get_time(), case_id, evidence_id, 'CHECKEDIN', 0, '')

		self.new_block(block_to_add)

	def checkout(self, evidence_id):
		located = None

		for block in self.chain:
			if block.evidence_id == evidence_id:
				located = block

		if located is not None:
			if located.state != "CHECKEDOUT":
				out_block = Block(self.calculate_hash(), get_time(), located.case_id, evidence_id, 'CHECKEDOUT', 0, '')

				self.new_block(out_block)
				print(out_block)
			else:
				print("ERROR: This item is already checked out")
		else:
			print("ERROR: item does not exist")

	def checkin(self):
		pass

	def run_command(self):
		arg = self.args
		command = arg.command

		if command == "init":
			self.init()

		elif command == "log":
			for block in self.chain:
				print(block)
				print()

		elif command == "add":
			self.add(arg.case_id, arg.item_id[0])

		elif command == "checkout":
			self.checkout(arg.item_id)

		else:
			print(f"Unknown command: {self.args.command}")
			sys.exit(1)


def main():
	driver = Blockchain()
	driver.run_command()
	driver.write_file()


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
