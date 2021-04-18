import etherscan.accounts as accounts
import sys
import time
import json

address_file = sys.argv[1]
n_days = int(sys.argv[2])
depth = int(sys.argv[3])

address_list = []

with open(address_file, 'r') as fin:
    items = json.loads(fin.read())
    for user_info in items["user"]:
        address_list.append(user_info["address"])
print("find %s address in start list" % (len(address_list)))


def days_to_now(timestamp):
    return (time.time()-int(timestamp))/3600/24

def get_all_address_trans_to(address):
    api = accounts.Account(address=address, api_key="DTTR16CPVKIE8XDIF4M6UB65J2X64Q77HS")
    transactions = api.get_all_transactions(offset=100, sort='asc', internal=False)
    from_address_set = set()
    for transaction in transactions:
        if "from" in transaction and transaction["from"] != address and days_to_now(transaction["timeStamp"]) <= n_days:
            from_address_set.add(transaction["from"])
    if address in from_address_set:
        from_address_set.remove(address)
    print("find %s address trans to %s" % (len(from_address_set), address))
    return from_address_set


def get_trans_records():
    trans_records = {}
    i = 1
    while i <= depth:
        for target_address in address_list:
            if target_address not in trans_records:
                addresses = get_all_address_trans_to(target_address)
                trans_records[target_address] = [addresses]
            else:
                next_level_addresses = {}
                for address in trans_records[target_address][-1]:
                    addresses = get_all_address_trans_to(address)
                    next_level_addresses.update(addresses)
                if target_address in next_level_addresses:
                    next_level_addresses.remove(target_address)
                trans_records[target_address].append(next_level_addresses)
            all_address = set()
            for address_set in trans_records[target_address]:
                all_address = all_address.union(address_set)
            print("depth %s, target address: %s, total pre address: %s" % (i, target_address, len(all_address)))
        i += 1
    return trans_records

trans_records = get_trans_records()
for target_address in trans_records:
    all_address = set()
    for address_set in trans_records[target_address]:
        all_address.union(address_set)
    trans_records[target_address] = all_address

writer = open("result.txt", 'w')
has_common_from = {}
all_targets = list(trans_records.keys())
for i in range(len(all_targets)):
    target1 = all_targets[i]
    from_adds1 = trans_records[target1]
    for j in range(i, len(all_targets)):
        target2 = all_targets[j]
        from_adds2 = trans_records[target2]
        common_from_adds = from_adds1.intersection(from_adds2)
        if len(common_from_adds) > 0:
            has_common_from[(target1, target2)] = list(common_from_adds)
            writer.write("%s, %s: \n"+"".join(["\t"+address+"\n" for address in common_from_adds]))
        print("%s and %s has %s trans address in common" % (target1, target2, len(common_from_adds)))











