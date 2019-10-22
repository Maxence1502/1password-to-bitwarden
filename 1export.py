#!/usr/bin/env python3

import subprocess as sp
import pprint
import json
import logging
import tempfile
import os
import csv


logging.basicConfig(level=logging.INFO)


OP_BIN = 'op'
ZIP_BIN = 'zip'


def main():
    dir_path = tempfile.mkdtemp(suffix='password-export')
    logging.info('Store temp files in ' + dir_path)
    vaults = retrieve_vaults()
    for vault in vaults:
        vault_name, records = process_vault(vault)      
        with open(os.path.join(dir_path, vault_name.lower()), 'w') as csvfile:
            record_writer = csv.writer(csvfile)
            for record in records:
                record_writer.writerow([
                    record['title'],
                    record['username'],
                    record['password'],
                    record['url']
                ])



def process_vault(vault):
    vault_uuid = vault['uuid']
    vault_name = vault['name']
    logging.info('Vault "{}": Fetch items'.format(vault_name))
    items = retrieve_items(vault_uuid)
    records = []
    logging.info('Vault "{}": {}/{}'.format(vault_name, 0, len(items)))
    for index, item in enumerate(items):
        item_data = retrieve_item(item['uuid'])
        extracted = extract_item_fields(item_data)
        records.append(extracted)
        logging.info('Vault "{}": {}/{}'.format(vault_name, index + 1, len(items)))
    return vault_name, records


def retrieve_vaults():
    data = catch_op_json(['op', 'list', 'vaults'])
    return data

def retrieve_items(vault_uuid): 
    data = catch_op_json(['op', 'list', 'items', '--vault=' + vault_uuid])
    return data


def retrieve_item(item_uuid):
    data = catch_op_json(['op', 'get', 'item', item_uuid])
    return data


def extract_item_fields(item_data):
    details = item_data.get('details', {})
    fields = details.get('fields', [])
    title = item_data.get('overview', {}).get('title', '')
    username = value_from_fields(fields, 'username')
    password = value_from_fields(fields, 'password') or details.get('password', '')
    url = item_data.get('overview', {}).get('url', '')
    return {
        'title': title,
        'username': username,
        'password': password,
        'url': url,
    }


def value_from_fields(item_fields, key):
    for f in item_fields:
        if f.get('designation', '') == key:
            return f.get('value', '')
    return ''


def catch_op_json(args):
    output = sp.run(args, check=True, stdout=sp.PIPE).stdout    
    return json.loads(output.decode('utf-8'))


if __name__ == '__main__':
    main()
