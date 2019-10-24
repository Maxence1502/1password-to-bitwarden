#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import csv
import json
import os
import shutil
import subprocess as sp
import tempfile
from collections import namedtuple


OP_BIN = 'op'
GPG_BIN = 'gpg'
TAR_BIN = 'tar'


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
    vaults = [process_vault(v) for v in retrieve_vaults()]
    # vaults = [
    #     Vault(title='t1', records=DUMMY_RECORD_SET),
    #     Vault(title='t2', records=DUMMY_RECORD_SET),
    #     Vault(title='t3', records=DUMMY_RECORD_SET),
    #     Vault(title='t4', records=DUMMY_RECORD_SET),
    # ]
    with tempfile.TemporaryDirectory(suffix='-one-password-export') as dir_path:
        print('Store temp files in {}'.format(dir_path))
        for vault in vaults:
            save_vault(dir_path, vault)
        encrypt_saved_data(dir_path, 'export', '123')
    print('Done')


def process_vault(vault):
    vault_uuid = vault['uuid']
    vault_name = vault['name']
    str_v = lambda v, m: '\rVault "{}": {:20}'.format(v, m)
    str_vr = lambda v, i, t: str_v(v, '{}/{}'.format(i, t))
    print(str_v(vault_name, 'fetch items'), end='')
    items = retrieve_items(vault_uuid)
    records = []
    print(str_vr(vault_name, 0, len(items)), end='')
    for index, item in enumerate(items):
        item_data = retrieve_item(item['uuid'])
        extracted = extract_item_fields(item_data)
        records.append(extracted)
        print(str_vr(vault_name, index + 1, len(items)), end='')
    print('')
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


def encrypt_saved_data(dir_path, file_name, password):
    gpg_name = file_name + '.tar.gpg'
    with tempfile.TemporaryDirectory(suffix='-one-password-export') as tar_dir_path:
        print('Store temp tar in ' + tar_dir_path)
        tar_name = os.path.join(tar_dir_path, file_name + '.tar')
        sp.run([TAR_BIN, '-cf', tar_name, '-C', dir_path, '.'])
        sp.run([GPG_BIN, '--symmetric', '--batch', '--yes', '--passphrase', password, 
            '--output', gpg_name, tar_name])


def retrieve_vaults():
    print('Fetch vault list')
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
