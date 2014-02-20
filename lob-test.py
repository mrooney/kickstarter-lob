#!/usr/bin/env python
import csv
import hashlib
import json
import lob
import shelve
import sys

config = json.loads("config.json")
lob.api_key = config['api_key']
postcard_from_address = config['postcard_from_address']
postcard_message = config['postcard_message']
postcard_front = config['postcard_front']
postcard_name = config['postcard_name']

class ParseKickstarterAddresses:
    def __init__(self, filename):
        self.items = []
        with open(filename, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                row['md5'] = self.dict_md5(reader.fieldnames, row)
                self.items.append(row)
                pass

    def dict_md5(self, keys, dictionary):
        '''Given an array of keys and a dict, returns md5 of dict'''
        line = []
        for key in keys:
            line.append(dictionary[key])
        m = hashlib.md5()
        m.update(str(line))
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
    history = shelve.open('lob_history')

    filename = sys.argv[1]
    addresses = ParseKickstarterAddresses(filename)

    for line in addresses.items[0:10]:
        md5 = line['md5']
        to_person = line['Shipping Name']
        if md5 in history:
            text = "Already processed entry for {} ({}), skipping"
            print(text.format(to_person, history[md5]))
            continue
        to_address = kickstarter_dict_to_lob_dict(line)
        try:
            lob.AddressVerify.verify(**to_address)
        except:
            msg = 'Error: Address Verification Failed'
            print("{} for {} ({})".format(msg, to_person, md5))
            history[md5] = msg
            history.sync()
            continue

        try:
            rv = lob.Postcard.create(to=to_address,
                                     name=postcard_name,
                                     from_address=postcard_from_address,
                                     front=postcard_front,
                                     message=postcard_message)
            job_id = rv.id
            history[md5] = job_id
            print("Postcard sent to {}! ({})".format(to_person, job_id))
        except:
            msg = 'Error: Failed to send postcard to Lob.com'
            print("{} for {}".format(msg, to_person))
            history[md5] = msg
            history.sync()
            continue

    history.close()

if __name__ == "__main__":
    main()
