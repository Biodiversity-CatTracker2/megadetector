#!/usr/bin/env python
# coding: utf-8

import os

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
    jb = JSONBin(bin_id=os.getenv('BIN_ID'), verbose=True)
    if not os.getenv('BIN_ID'):
        jb.create_bin()
