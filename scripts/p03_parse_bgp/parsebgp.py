import ipaddress
import re
from ruamel.yaml import YAML


def strict_parse(line):
    """ strict parse
    function that takes the data from the bgp table and parses it strictly
    this will break with any kind of alteration, aka this will not work with
    a cisco based output """

    # store all valid addresses in list
    valid_addresses = []

    # assume the ipaddress is the first word in the output!
    route_address = line.split()[0]

    # remove ">" if it exists in a strict manner
    if route_address.startswith('>'):
        route_address = route_address.strip('>')

    # store address in valid addresses
    valid_addresses.append(route_address)

    # assume the next hop address is second word
    next_hop_address = line.split()[1]

    # store address in valid addresses
    valid_addresses.append(next_hop_address)

    return valid_addresses

def check_if_ipv4address(potential_address):
    """ check if ipv4address
    this is used in conjunction with the flexible parse function
    and determines if the word is an ipaddress in a smart way """

    try:
        ipaddress.IPv4Interface(potential_address)
        return True
    except ipaddress.AddressValueError:
        return False

def flexible_parse(line):
    """ flexible parse
    function that will take the data from the bgp table and determine
    validity by checking the address if it is a valid ip address! """

    # regex compile removals of any character (except '.' and '/')
    remove_special_char = re.compile(r'[^\d./]+')

    # store all valid addresses in list
    valid_addresses = []

    # iterate through the words in the line and find all addresses
    # there should be two in total generally speaking, but depending
    # on the format of the show ip bgp command, this may not necessarily
    # be true so we must account for this!

    for word in line.split():
        # strip any symbols from output except '.'
        word = remove_special_char.sub('', word)

        # check if our word is a valid address!
        if check_if_ipv4address(word):
            valid_addresses.append(word)


    return valid_addresses

def bgp_parse_logic(filename):
    """ bgp parse logic
    parse function to run in this example exercise """

    # initialize final reliability datastructure
    bgp_db = {}

    # initialize basic variables
    route_address = ''
    next_hop_address = ''

    with open(filename, 'r') as fn:
        # iterate through the file
        for line in fn:
            # store valid addresses
            valid_addresses = flexible_parse(line)
            print(valid_addresses)
            #valid_addresses = strict_parse(line)

            # check number of valid addresses is 2
            if len(valid_addresses) == 2:
                # initialize the valid addresses
                route_address = valid_addresses[0]
                next_hop_address = valid_addresses[1]

                # initialize route address in dictionary if not already done
                if route_address not in bgp_db:
                    bgp_db[route_address] = 0

                # increment redundancy count
                bgp_db[route_address] += 1

            # check number of valid addresses is 1
            # this should only be invoked with a different format of
            # 'show ip bgp' - aka CISCO DEVICES
            # this will also break strict parsing FYI
            elif len(valid_addresses) == 1:
                # initialize valid addresses
                next_hop_address = valid_addresses[0]

                # initialize route address in dictionary if not already done
                if route_address not in bgp_db:
                    bgp_db[route_address] = 0

                # increment redundancy count
                bgp_db[route_address] += 1


    # save our data as a yaml file to be reused for graping purposes!
    with open('fullbgpredundancy.yml', 'w') as fn:
        yaml=YAML()
        yaml.default_flow_style = False
        yaml.dump(bgp_db, fn)

def main():
    # replace the below string with your filename
    bgp_parse_logic('bgptable.txt')

if __name__ == '__main__':
    main()