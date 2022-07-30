#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import csv
import json
import os
import subprocess as sp
import tempfile
from collections import namedtuple

OP_BIN = 'op'
GPG_BIN = 'gpg'
TAR_BIN = 'tar'

Record = namedtuple('Record', [
    'Title',
    'Url',
    'Username',
    'Password',
    'OTPAuth',
    'Favorite',
    'Archived',
    'Tags',
    'Notes',
])

Vault = namedtuple('Vault', ['title', 'records'])


def main():
    args = parse_args()
    output_file_name = os.path.abspath(args.file_name)
    vaults = [process_vault(v) for v in retrieve_vaults()]

    with tempfile.TemporaryDirectory(suffix='-one-password-export') as dir_path:
        print('Store temp files in {}'.format(dir_path))
        for vault in vaults:
            save_vault(dir_path, vault)
        if args.password:
            export_encrypted(dir_path, output_file_name, args.password)
        else:
            export_plain(dir_path, output_file_name)
    print('Done')


def parse_args():
    parser = argparse.ArgumentParser(description='Export 1password logins')
    parser.add_argument('file_name', type=str,
                        help='output file name')
    parser.add_argument('--password', dest='password',
                        help='encrypt data')
    return parser.parse_args()


def process_vault(vault):
    vault_uuid = vault['id']
    vault_name = vault['name']
    str_v = lambda v, m: '\rVault "{}": {:20}'.format(v, m)
    str_vr = lambda v, i, t: str_v(v, '{}/{}'.format(i, t))
    print(str_v(vault_name, 'fetch items'), end='')
    items = retrieve_items(vault_uuid)
    records = []
    records.append(Record("Title","Url","Username","Password","OTPAuth","Favorite","Archived","Tags","Notes"))
    print(str_vr(vault_name, 0, len(items)), end='')
    for index, item in enumerate(items):
        item_data = retrieve_item(item['id'])
        extracted = extract_item_fields(item_data)
        records.append(extracted)
        print(str_vr(vault_name, index + 1, len(items)), end='')
    print('')
    return Vault(title=vault_name, records=records)


def save_vault(base_dir, vault):
    file_name = os.path.join(base_dir, vault.title.lower())
    with open(file_name, 'w') as csv_file:
        record_writer = csv.writer(csv_file)
        for record in vault.records:
            record_writer.writerow([
                record.Title,
                record.Url,
                record.Username,
                record.Password,
                record.OTPAuth,
                record.Favorite,
                record.Archived,
                record.Tags,
                record.Notes
            ])


def export_plain(dir_path, file_name):
    sp.run([TAR_BIN, '-cf', file_name + '.tar', '-C', dir_path, '.'])


def export_encrypted(dir_path, file_name, password):
    gpg_name = file_name + '.tar.gpg'
    with tempfile.TemporaryDirectory(suffix='-one-password-export') as tar_dir_path:
        tar_name = os.path.join(tar_dir_path, os.path.basename(file_name) + '.tar')
        print('Store temp tar in ' + tar_name)
        sp.run([TAR_BIN, '-cf', tar_name, '-C', dir_path, '.'])
        sp.run([GPG_BIN, '--symmetric', '--batch', '--yes', '--passphrase', password,
                '--output', gpg_name, tar_name])


def retrieve_vaults():
    print('Fetch vault list')
    data = catch_op_json([OP_BIN, 'vault', 'list', '--format=json'])
    return data


def retrieve_items(vault_uuid):
    data = catch_op_json([OP_BIN, 'item', 'list', '--vault=' + vault_uuid, '--format=json'])
    return data


def retrieve_item(item_uuid):
    data = catch_op_json([OP_BIN, 'item', 'get', item_uuid, '--format=json'])
    return data


def extract_item_fields(item_data):
    fields = item_data.get('fields', [])
    return Record(
        Title=item_data.get('title', ''),
        Url=(item_data.get('urls', [])[0]["href"] if item_data.get('urls', [])[0] else ''),
        Username=value_from_fields(fields, 'username').strip(),
        Password=value_from_fields(fields, 'password').strip(),
        OTPAuth="",
        Favorite="false",
        Archived="false",
        Tags="",
        Notes=value_from_fields(fields, 'notesPlain')
    )


def value_from_fields(item_fields, key):
    for f in item_fields:
        if f.get('id', '') == key:
            return f.get('value', '')
    return ''


def catch_op_json(args):
    output = sp.run(args, check=True, stdout=sp.PIPE).stdout
    return json.loads(output.decode('utf-8'))


if __name__ == '__main__':
    main()
