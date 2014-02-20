#!/usr/bin/env python
import csv
import hashlib
import json
import lob
import sys

class ParseKickstarterAddresses:
    def __init__(self, filename):
        self.items = []
        with open(filename, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                self.items.append(row)

def addr_str(addr):
    return u"{name}|{address_line1}|{address_line2}|{address_city}|{address_state}|{address_zip}|{address_country}".format(**addr).upper() 

def addr_md5(addr):
    m = hashlib.md5()
    m.update(addr_str(addr))
    return m.hexdigest()

def kickstarter_dict_to_lob_dict(dictionary):
    ks_to_lob = {'Shipping Name': 'name',
                 'Shipping Address 1': 'address_line1',
                 'Shipping Address 2': 'address_line2',
                 'Shipping City': 'address_city',
                 'Shipping State': 'address_state',
                 'Shipping Postal Code': 'address_zip',
                 'Shipping Country': 'address_country'}
    address_dict = {}
    for key in ks_to_lob.keys():
        address_dict[ks_to_lob[key]] = dictionary[key]
    return address_dict

def main():
    filename = sys.argv[1]
    config = json.load(open("config.json"))
    lob.api_key = config['api_key']

    print("Fetching list of any postcards already sent...")
    processed_md5s = set()
    for processed in lob.Postcard.list():
        md5 = addr_md5(processed.to.to_dict())
        processed_md5s.add(md5)

    postcard_from_address = config['postcard_from_address']
    postcard_message = config['postcard_message']
    postcard_front = config['postcard_front']
    postcard_name = config['postcard_name']

    addresses = ParseKickstarterAddresses(filename)

    to_send = []
    already_sent = []

    print("Verifying addresses of backers...")
    for line in addresses.items:#[:10]
        to_person = line['Shipping Name']
        to_address = kickstarter_dict_to_lob_dict(line)
        try:
            to_name = to_address['name']
            to_address = lob.AddressVerify.verify(**to_address).to_dict()['address']
            to_address['name'] = to_name
        except lob.exceptions.LobError:
            msg = 'warning: address verification failed for {}, cannot send to this backer.'
            print(msg.format(line['Email']))
            continue

        md5 = addr_md5(to_address)
        if md5 in processed_md5s:
            already_sent.append(to_address)
        else:
            to_send.append(to_address)

    nbackers = len(addresses.items)
    print("Already sent postcards to {} of {} backers".format(len(already_sent), nbackers))
    if not to_send:
        print("SUCCESS: All backers with verified addresses have been processed, you're done!")
        return

    query = "Send to {} unsent backers now? [y/N]: ".format(len(to_send), nbackers)
    if raw_input(query).lower() == "y":
        successes = failures = 0
        for to_address in to_send:
            try:
                rv = lob.Postcard.create(to=to_address, name=postcard_name, from_address=postcard_from_address, front=postcard_front, message=postcard_message)
                print("Postcard sent to {}! ({})".format(to_address['name'], rv.id))
                successes += 1
            except lob.exceptions.LobError:
                msg = 'Error: Failed to send postcard to Lob.com'
                print("{} for {}".format(msg, to_address['name']))
                failures += 1
        print("Successfully sent to {} backers with {} failures".format(successes, failures))
    else:
        print("Okay, not sending to unsent backers.")


if __name__ == "__main__":
    main()
