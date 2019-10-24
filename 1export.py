#!/usr/bin/env python3

from collections import namedtuple
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

Record = namedtuple('Record', [
    'title', 
    'username',
    'password',
    'url',
])

Vault = namedtuple('Vault', ['title', 'records'])
    
DUMMY_RECORD_SET = [
    Record(
        title='title' + str(i),
        username='username' + str(i),
        password='password' + str(i),
        url='url' + str(i),
    )
    for i in range(10)
]

def main():
    # dir_path = tempfile.mkdtemp(suffix='password-export')
    dir_path = './tmp'
    vaults = [Vault(title='test', records=DUMMY_RECORD_SET)]
    for vault in vaults:
        save_vault(dir_path, vault)


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
    return Vault(title=vault_name, records=records)


def save_vault(base_dir, vault):
    file_name = os.path.join(base_dir, vault.title.lower())
    with open(file_name, 'w') as csvfile:
        record_writer = csv.writer(csvfile)
        for record in vault.records:
            record_writer.writerow([
                record.title,
                record.username,
                record.password,
                record.url
            ])


def retrieve_vaults():
    data = catch_op_json([OP_BIN, 'list', 'vaults'])
    return data

def retrieve_items(vault_uuid): 
    data = catch_op_json([OP_BIN, 'list', 'items', '--vault=' + vault_uuid])
    return data


def retrieve_item(item_uuid):
    data = catch_op_json([OP_BIN, 'get', 'item', item_uuid])
    return data


def extract_item_fields(item_data):
    details = item_data.get('details', {})
    fields = details.get('fields', [])
    overview = item_data.get('overview', {})
    username = value_from_fields(fields, 'username')
    password = value_from_fields(fields, 'password') or details.get('password', '')
    return Record(
        title=overview.get('title', ''),
        username=username,
        password=password,
        url=overview.get('url', ''),
    )


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
