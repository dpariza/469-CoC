import argparse
import sys


#print("Usage: bchoc [log | remove] [-r] [-n num_entries] [-c case_id] [-i item_id]")


# parse bchoc
parser = argparse.ArgumentParser(description='Process bchoc commands')
parser.add_argument('bchoc', help='Main command')

# create subparsers for 'log' and 'remove' commands
subparsers = parser.add_subparsers(dest='command')

# subparser for 'add' command
add_parser = subparsers.add_parser('add', help='Add a new evidence item to the blockchain and associate it with the given case identifier')
add_parser.add_argument('-c', '--case_id', required=True, type=int, help='Case ID to bchoc block')
add_parser.add_argument('-i', '--item_id', nargs='+', required=True, type=int, help='Item ID of block')

# subparser for 'checkout' command
checkout_parser = subparsers.add_parser('checkout', help='Add a new checkout entry to the chain of custody for the given evidence item')
checkout_parser.add_argument('-i', '--item_id', required=True, type=int, help='Item ID of block')

# subparser for 'checkin' command
checkin_parser = subparsers.add_parser('checkin', help=' Add a new checkin entry to the chain of custody for the given evidence item')
checkin_parser.add_argument('-i', '--item_id', required=True, type=int, help='Item ID of block')

# subparser for 'log' command
log_parser = subparsers.add_parser('log', help='Display the blockchain entries giving the oldest first (unless -r is given)')
log_parser.add_argument('-r', '--reverse', action='store_true', help='Reverse the order of blocks')
log_parser.add_argument('-n', '--num_entries', type=int, help='Number of blocks to show')
log_parser.add_argument('-c', '--case_id', required=True, type=int, help='Case ID to bchoc block')
log_parser.add_argument('-i', '--item_id', required=True, type=int, help='Item ID of block')

# subparser for 'remove' command
remove_parser = subparsers.add_parser('remove', help='Prevents any further action from being taken on the evidence item specified')
remove_parser.add_argument('-i', '--item_id', type=int, required=True, help='ID of block to remove')
remove_parser.add_argument('-y', '--reason', required=True, help='Reason for removal')
remove_parser.add_argument('-o', '--owner', help='Owner')


# subparser for 'init' command
init_parser = subparsers.add_parser('init', help='init Sanity check. Only starts up and checks for the initial block')


# subparser for 'verify' command
verify_parser = subparsers.add_parser('verify', help='Parse the blockchain and validate all entries')

args = parser.parse_args()

if args.command == "log":
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



else:
    #print(f"Unknown command: {args.command}")
    sys.exit(1)

