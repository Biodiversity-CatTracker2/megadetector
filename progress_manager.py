#!/usr/bin/env python
# coding: utf-8

import argparse
import json
import os
import sys
from glob import glob
from pathlib import Path


class Progress:

    def __init__(self, data_dir, progress_file='progress.json', verbose=False):
        self.data_dir = data_dir
        self.progress_file = progress_file
        self.verbose = verbose

    def scan_subdirs(self):

        def scan(_dir):
            return [x.path for x in os.scandir(_dir) if x.is_dir()]

        subdirs = scan(self.data_dir)
        return [x for x in sum([scan(_dir) for _dir in subdirs], []) if x]

    def create_progress_file(self):
        print('Creating a `progress.json` file...')
        subdirs = self.scan_subdirs()
        subdirs = [x for x in subdirs if Path(x).name != 'output']
        for _subdir in subdirs:
            if all(Path(x).is_dir() for x in glob(f'{_subdir}/*')):
                subdirs.remove(_subdir)
        subdirs_dict = {k: False for k in subdirs}
        with open(self.progress_file, 'w') as j:
            json.dump(subdirs_dict, j, indent=4)

        if self.verbose:
            print(json.dumps(subdirs_dict, indent=4))
        print('Done!')
        return subdirs_dict

    def update_progress(self, data):
        with open(self.progress_file) as j:
            progress_data = json.load(j)

        progress_data.update(data)

        with open(self.progress_file, 'w') as j:
            json.dump(progress_data, j, indent=4)

        if self.verbose:
            print(json.dumps(progress_data, indent=4))
        return progress_data

    def status(self, relative_folder_path):
        with open(self.progress_file) as j:
            progress_data = json.load(j)
        return progress_data.get(relative_folder_path)

    def show_progress(self):
        print('Calculating estimated progress...')
        num_all_images = 0

        with open(self.progress_file) as j:
            progress_data = json.load(j)

        for folder in progress_data:
            num_all_images += len(
                [x for x in glob(f'{folder}/*') if not Path(x).is_dir()])

        json_data_files = glob(f'{self.data_dir}/**/data*.json',
                               recursive=True)
        num_finished_files = 0
        for file in json_data_files:
            with open(file) as j:
                data = json.load(j)
                num_finished_files += len(data['images'])

        print('\nEstimated progress:')
        p = f'({round(100 * num_finished_files / num_all_images, 2)}%)'
        print(f'\tProcessed images: {num_finished_files}/{num_all_images} {p}')
        return


def opts() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument('-d',
                        '--data-dir',
                        help='Path to the data directory',
                        type=str,
                        required=True)
    parser.add_argument('--create',
                        help='Create a progress file',
                        action='store_true')
    parser.add_argument('--show-progress',
                        action='store_true',
                        help='Show current progress')
    parser.add_argument('--progress-file',
                        help='Path to the progress JSON file',
                        type=str,
                        default='progress.json')
    parser.add_argument('--verbose',
                        help='Print lots more stuff',
                        action='store_true')
    return parser.parse_args()


if __name__ == '__main__':
    args = opts()

    print(f'Data directory: {args.data_dir}')
    assert Path(args.data_dir).exists(
    ), 'The directory path you passed does not exist!'

    if not args.create and not args.show_progress:
        sys.exit('No options were passed...')

    progress = Progress(data_dir=args.data_dir,
                        progress_file=args.progress_file,
                        verbose=args.verbose)

    if args.create:
        progress.create_progress_file()

    if args.show_progress:
        progress.show_progress()
