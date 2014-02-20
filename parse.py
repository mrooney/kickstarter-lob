#!/usr/bin/env python
import csv
import sys
import pprint
import hashlib


def dict_md5(keys, dictionary):
    line = []
    for key in keys:
        line.append(dictionary[key])
    m = hashlib.md5()
    m.update(str(line))
    return m.hexdigest()

filename = sys.argv[1]

lines = []
with open(filename, 'r') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        row['md5'] = dict_md5(reader.fieldnames, row)
        lines.append(row)


for line in lines:
    backer_name = line['Backer Name']
    shipping_name = line['Shipping Name']

    if backer_name != shipping_name:
        print "Backer: '{}' Shipper: '{}'".format(backer_name, shipping_name)

sys.exit()


for line in lines:
    print("Backer Name: {}".format(line['Backer Name']))
    print("Name: {}".format(line['Shipping Name']))
    parts = []
    x = ['Address 1', 'Address 2', 'City', 'State', 'Postal Code', 'Country']
    for field in x:
        key = "Shipping {}".format(field)
        if line[key]:
            parts.append(line[key])
    address = ', '.join(parts)
    print("Address: {}".format(address))
