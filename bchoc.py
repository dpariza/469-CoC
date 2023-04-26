#!/usr/bin/env python3

import os
import sys
import struct
import hashlib
import time
from datetime import datetime
import uuid
import copy
import argparse


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
		self.filepath = ''

	def __str__(self):
		return 'Previous Hash: {}\nTimestamp: {}\nCase ID: {}\nEvidence ID: {}\nState: {}\nData Length: {}\nData: {}'.format(
			self.previous_hash, datetime.fromtimestamp(self.timestamp).isoformat() + 'Z', uuid.UUID(self.case_id),
			self.evidence_id, self.state, self.data_length, self.data)


def get_time():
	return round(time.time(), 6)


def load_file():
	env_path = os.environ.get("BCHOC_FILE_PATH")

	try:
		with open(env_path, 'rb'):
			filepath = env_path
	except:
		with open(env_path, 'wb'):
			pass

	return env_path


def unpack_bytes(unpack_this, data_length):
	if len(unpack_this) != (76 + data_length):
		print("ERROR: pre-existing file is invalid")
		exit(1)

	unpacked = struct.unpack(f'32s d 16s I 12s I {data_length}s', unpack_this)

	hash_unpacked = str(hex(int.from_bytes(unpacked[0], "little")))[2:]

	if hash_unpacked == '0':
		hash_unpacked = '0000000000000000000000000000000000000000000000000000000000000000'

	case_unpacked = str(hex(int.from_bytes(unpacked[2], "little")))[2:]

	while len(case_unpacked) < 32:
		case_unpacked = '0' + case_unpacked

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
	case_as_int = int(cur.case_id.replace('-', ''), 16)
	case_as_int = case_as_int.to_bytes(16, "little")

	return_bytes = struct.pack(f'32s d 16s I 12s I {cur.data_length}s', hash_as_int,
							   cur.timestamp, case_as_int, cur.evidence_id, bytes(cur.state, 'utf-8'),
							   cur.data_length, bytes(cur.data, 'utf-8'))
	return return_bytes


def parse_file(filepath):
	chain = []

	# unpacks init block
	with open(filepath, 'rb') as f:
		if not f.peek(90):
			print("ERROR: invalid INIT block")
			exit(1)
		info = f.read(90)

		# unpacks init block, data length preset as 14
		chain.append(unpack_bytes(info, 14))

		# this works for checking following blocks, make it less ugly
		while continues := f.peek(76):

			if not f.peek(76):
				print("ERROR: invalid block after INIT")
				exit(1)

			next_data_length = continues[72:76]

			if len(next_data_length) != 4:
				print("ERROR: invalid block after INIT")
				exit(1)

			next_data_length = struct.unpack('I', next_data_length)[0]

			if not f.peek(76 + next_data_length):
				print("ERROR: invalid block after INIT")
				exit(1)

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
		return chain, False, filepath

	else:

		blockchain = parse_file(filepath)

		# True flag denotes successful load of existing init block
		return blockchain, True, filepath


class Blockchain:

	def __init__(self):
		setup = setup_blockchain()
		self.chain = setup[0]
		self.init_flag = setup[1]
		self.filepath = setup[2]
		self.error_state = False
		self.error_message = 'CLEAN'
		self.args = process_commands()
		if self.args.command == "add" or self.args.command == "log":
			if self.args.case_id:
				self.args.case_id = self.args.case_id.replace('-', '')

	def write_file(self):

		with open(self.filepath, 'ab') as f:
			for block in self.chain:
				if block.new_item:
					write_bytes = pack_bytes(block)
					f.write(write_bytes)

	def init(self):
		if self.init_flag:
			print("Blockchain file found with INITIAL block.")
		else:
			print("Blockchain file not found. Created INITIAL block.")

	def log_printer(self, block):
		arg = self.args

		print('Case: ' + str(uuid.UUID(block.case_id)))

		if arg.command == 'log':

			print('Item: ' + str(block.evidence_id))
			print('Action: ' + block.state)
			print('Time: ' + datetime.fromtimestamp(block.timestamp).isoformat() + 'Z')
			print()

		elif arg.command == 'add':

			print('Added item: ' + str(block.evidence_id))
			print('Status: ' + block.state)
			print('Time of action: ' + datetime.fromtimestamp(block.timestamp).isoformat() + 'Z')
			print()

		elif arg.command == 'remove':

			print('Removed item: ' + str(block.evidence_id))
			print('Status : ' + block.state)

			if arg.why == 'RELEASED':
				print('Owner info: ' + arg.owner)

			print('Time of action: ' + datetime.fromtimestamp(block.timestamp).isoformat() + 'Z')
			print()

		elif arg.command == 'checkout':

			print('Checked out item: ' + str(block.evidence_id))
			print('Status: ' + block.state)
			print('Time of action: ' + datetime.fromtimestamp(block.timestamp).isoformat() + 'Z')
			print()

		elif arg.command == 'checkin':

			print('Checked in item: ' + str(block.evidence_id))
			print('Status: ' + block.state)
			print('Time of action: ' + datetime.fromtimestamp(block.timestamp).isoformat() + 'Z')
			print()

	def log(self):
		arg = self.args
		iterator = copy.copy(self.chain)
		count = 0
		maximum = 100000000

		if arg.reverse:
			iterator.reverse()

		if arg.num_entries:
			maximum = arg.num_entries

		if arg.item_id:
			for block in iterator:
				if block.evidence_id == arg.item_id and count < maximum:
					self.log_printer(block)
					count = count + 1

		elif arg.case_id:
			for block in iterator:
				if block.case_id == arg.case_id and count < maximum:
					self.log_printer(block)
					count = count + 1
		else:
			for block in iterator:
				if count < maximum:
					self.log_printer(block)
					count = count + 1

	def calculate_hash(self):
		prev = self.chain[-1]
		raw_hashing = prev.previous_hash + str(prev.timestamp) + prev.case_id + str(
			prev.evidence_id) + prev.state + str(prev.data_length) + prev.data
		raw_hashing = raw_hashing.encode('utf-8')

		prev_hash = hashlib.sha256(raw_hashing).digest()
		prev_hash = str(hex(int.from_bytes(prev_hash, "little")))

		return prev_hash

	def new_block(self, block_to_add):
		# do all the checks for appending the chain here!
		if block_to_add.state == "CHECKEDIN" or block_to_add.state == "CHECKEDOUT":
			for block in self.chain:
				if block.evidence_id == block_to_add.evidence_id and (
						block.state == 'DISPOSED' or block.state == 'DESTROYED' or block.state == 'RELEASED'):
					self.end("ERROR: added item after it was removed")

		block_to_add.new_item = True
		self.chain.append(block_to_add)

	def add(self):
		arg = self.args

		for item_id in arg.item_id:
			block_to_add = Block(self.calculate_hash(), get_time(), arg.case_id, item_id, 'CHECKEDIN',
								 0, '')

			located = None
			iterator = reversed(copy.copy(self.chain))
			for block in iterator:
				if block.evidence_id == item_id:
					located = block
					break

			if located is not None and located.state == 'CHECKEDIN':
				self.end("ERROR: duplicate entry to chain detected")

			self.new_block(block_to_add)
			self.log_printer(block_to_add)

	def checkout(self, evidence_id):
		located = None
		# print()

		for block in self.chain:
			if block.evidence_id == evidence_id:
				located = block

		if located is not None:
			if located.state != "CHECKEDOUT":
				out_block = Block(self.calculate_hash(), get_time(), located.case_id, evidence_id, 'CHECKEDOUT', 0, '')

				self.new_block(out_block)
				self.log_printer(out_block)
			else:
				self.end("ERROR: This item is already checked out!!!")
		else:
			self.end("ERROR: item does not exist")

	def checkin(self, evidence_id):
		located = None

		for block in self.chain:
			if block.evidence_id == evidence_id:
				located = block

		if located is not None:
			if located.state != "CHECKEDIN":
				out_block = Block(self.calculate_hash(), get_time(), located.case_id, evidence_id, 'CHECKEDIN', 0, '')

				self.new_block(out_block)
				self.log_printer(out_block)
			else:
				self.end("ERROR: This item is already checked in!!!")
		else:
			self.end("ERROR: item does not exist")

	def remove(self, evidence_id):
		arg = self.args
		located = None

		for block in self.chain:
			if block.evidence_id == evidence_id:
				located = block

		if located is not None:
			if located.state == "CHECKEDIN" and (
					arg.why == 'DISPOSED' or arg.why == 'DESTROYED' or arg.why == 'RELEASED'):
				data = ''
				data_length = 0

				if arg.why == 'RELEASED':
					if arg.owner:
						data = arg.owner
						data_length = len(data) + 1
					else:
						self.end("ERROR: Must provide owner info when releasing block")

				out_block = Block(self.calculate_hash(), get_time(), located.case_id,
								  evidence_id, arg.why, data_length, data)

				self.new_block(out_block)

				self.log_printer(out_block)
			else:
				self.end("ERROR: This item is not checked in!!!")
		else:
			self.end("ERROR: item does not exist")

	def print_checksums(self):
		for i in range(0, len(self.chain), 1):
			print(str(i) + ": " + self.chain[i].previous_hash)

		par = self.chain[0]
		parent_content = par.previous_hash + str(par.timestamp) + par.case_id + str(par.evidence_id) + par.state + str(
			par.data_length) + par.data

	def check_after_remove(self):
		iterator = 1
		for block in self.chain:
			if block.state == 'DISPOSED' or block.state == 'DESTROYED' or block.state == 'RELEASED':
				for i in range(iterator, len(self.chain), 1):
					if self.chain[i].evidence_id == block.evidence_id:
						self.end("ERROR: an item was modified after previous removal OR never added properly")
			iterator = iterator + 1

	def checked_twice(self):
		iterator = 1
		for block in self.chain:
			for i in range(iterator, len(self.chain), 1):
				if self.chain[i].evidence_id == block.evidence_id:
					if self.chain[i].state == block.state:
						self.end("ERROR: duplicated detected (added twice/checked in or out twice)")
					else:
						break
			iterator = iterator + 1

	def remove_before_add(self):
		iterator = reversed(copy.copy(self.chain))

		for block in iterator:
			if block.state == 'DISPOSED' or block.state == 'DESTROYED' or block.state == 'RELEASED':
				found = False
				for block2 in self.chain:
					if block is block2 and not found:
						self.end("ERROR: item removed without being added")
					else:
						if block.evidence_id == block.evidence_id:
							found = True

	def bad_remove(self):
		for block in self.chain:
			#ignore initial block for state checks
			if block.previous_hash == '0000000000000000000000000000000000000000000000000000000000000000':
				continue

			if block.state == 'RELEASED':
				if block.data == '':
					self.end("ERROR: item released without an owner provided")
			elif block.state != 'CHECKEDIN' and block.state != 'CHECKEDOUT' and block.state != 'DESTROYED' and block.state != 'DISPOSED':
				self.end("ERROR: item released with invalid why")


	def unique_parents(self):
		iterator = 1
		for block in self.chain:
			for i in range(iterator, len(self.chain), 1):
				if block.previous_hash == self.chain[i].previous_hash:
					self.end("ERROR: Duplicate parents detected")
			iterator = iterator + 1

	def verify(self):
		print(f"Transactions in blockchain: {len(self.chain)}")

		# validation code here
		self.remove_before_add()
		self.check_after_remove()
		self.checked_twice()
		self.bad_remove()
		self.unique_parents()

		print("State of blockchain: CLEAN")

	def end(self, message):
		print(message)
		exit(1)

	def run_command(self):
		arg = self.args
		command = arg.command

		if command == "init":
			self.init()

		elif command == "log":
			self.log()

		elif command == "add":
			if not arg.case_id:
				self.end("No case id given")
			elif not arg.item_id:
				self.end("No item id given")
			else:
				self.add()

		elif command == "checkout":
			self.checkout(arg.item_id)

		elif command == "checkin":
			self.checkin(arg.item_id)

		elif command == "remove":
			self.remove(arg.item_id)

		elif command == "verify":
			self.verify()

		else:
			print(f"Unknown command: {self.args.command}")
			sys.exit(1)


def main():
	driver = Blockchain()
	driver.run_command()
	driver.write_file()




def process_commands():
	# parse bchoc
	parser = argparse.ArgumentParser(description='Process bchoc commands')
	# parser.add_argument('bchoc', help='Main command')

	# create subparsers for 'log' and 'remove' commands
	subparsers = parser.add_subparsers(dest='command')

	# subparser for 'add' command
	add_parser = subparsers.add_parser('add',
									   help='Add a new evidence item to the blockchain and associate it with the given case identifier')
	add_parser.add_argument('-c', '--case_id', type=str,
							help='Specifies the case identifier that the evidence is associated with')
	add_parser.add_argument('-i', '--item_id', action='append', type=int,
							help=' Specifies the evidence item’s identifier')

	# subparser for 'checkout' command
	checkout_parser = subparsers.add_parser('checkout',
											help='Add a new checkout entry to the chain of custody for the given evidence item')
	checkout_parser.add_argument('-i', '--item_id', required=True, type=int,
								 help=' Specifies the evidence item’s identifier')

	# subparser for 'checkin' command
	checkin_parser = subparsers.add_parser('checkin',
										   help=' Add a new checkin entry to the chain of custody for the given evidence item')
	checkin_parser.add_argument('-i', '--item_id', required=True, type=int,
								help=' Specifies the evidence item’s identifier!')

	# subparser for 'log' command
	log_parser = subparsers.add_parser('log',
									   help='Display the blockchain entries giving the oldest first (unless -r is given)')
	log_parser.add_argument('-r', '--reverse', action='store_true',
							help='Reverses the order of the block entries to show the most recent entries first')
	log_parser.add_argument('-n', '--num_entries', type=int,
							help='When used with log, shows num_entries number of block entries')
	log_parser.add_argument('-c', '--case_id', type=str,
							help='Specifies the case identifier that the evidence is associated with')
	log_parser.add_argument('-i', '--item_id', type=int, help=' Specifies the evidence item’s identifier')

	# subparser for 'remove' command
	remove_parser = subparsers.add_parser('remove',
										  help='Prevents any further action from being taken on the evidence item specified')
	remove_parser.add_argument('-i', '--item_id', type=int, required=True, help='ID of block to remove')
	remove_parser.add_argument('-y', '--why', required=True, help='Reason for the removal of the evidence item')
	remove_parser.add_argument('-o', '--owner',
							   help=': Information about the lawful owner to whom the evidence was released')

	# subparser for 'init' command
	init_parser = subparsers.add_parser('init',
										help='init Sanity check. Only starts up and checks for the initial block')

	# subparser for 'verify' command
	verify_parser = subparsers.add_parser('verify', help='Parse the blockchain and validate all entries')

	args = parser.parse_args()
	return args


if __name__ == "__main__":
	main()
