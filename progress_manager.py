#!/usr/bin/env python
# coding: utf-8

import json
import os
import sys
from glob import glob
from pathlib import Path

import requests
from dotenv import load_dotenv
from loguru import logger


class JSONBin:

    def __init__(self, bin_id=os.getenv('BIN_ID'), verbose=False):
        self.bin_id = bin_id
        self.verbose = verbose

    def api_request(self, method=None, data=None):
        headers = {
            'Content-Type': 'application/json',
            'X-Master-Key': os.environ['JSONBIN_KEY']
        }

        if self.bin_id:
            url = f'https://api.jsonbin.io/v3/b/{self.bin_id}'
        else:
            url = 'https://api.jsonbin.io/v3/b/'
            headers.update({'X-Bin-Name': 'data'})

        if self.verbose:
            logger.debug(f'Request: {url} {data}')

        if method == 'post':
            resp = requests.post(url, json=data, headers=headers)
        elif method == 'put':
            resp = requests.put(url, json=data, headers=headers)
        else:
            resp = requests.get(url, headers=headers)

        if self.verbose:
            logger.debug(f'Response: {resp.json()}')
        return resp

    def create_bin(self):
        data = {'_': True}
        resp = self.api_request(method='post', data=data)
        bin_id = resp.json()['metadata']['id']
        print(f'Bin ID: {bin_id}')
        return bin_id

    def update_bin(self, data):
        read_resp = self.api_request()
        record = read_resp.json()['record']
        record.update(data)
        if record.get('_'):
            record.pop('_')
        put_resp = self.api_request(method='put', data=record)
        return put_resp.json()

    def status(self, relative_folder_path):
        record = self.api_request().json()['record']
        return record.get(relative_folder_path)


if __name__ == '__main__':
    load_dotenv()
    jb = JSONBin(bin_id=os.getenv('BIN_ID'), verbose=False)
    if not os.getenv('BIN_ID'):
        jb.create_bin()

    elif '--show-bin' in sys.argv:
        record = jb.api_request().json()['record']
        print(json.dumps(record, indent=4))

    elif '--show-progress' in sys.argv:
        print('Calculating estimated progress...')
        all_files = glob(f'data/**/*', recursive=True)
        num_all_files = len([x for x in all_files if not Path(x).is_dir()])

        json_data_files = glob(f'data/**/data*.json', recursive=True)
        num_finished_files = 0
        for file in json_data_files:
            with open(file) as j:
                data = json.load(j)
                num_finished_files += len(data['images'])

        print('\nEstimated pogress:')
        p = f'({round(100 * num_finished_files / num_all_files, 2)}%)'
        print(f'\tProcessed images: {num_finished_files}/{num_all_files} {p}')
