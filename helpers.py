import argparse
import json
import shlex
import subprocess
import sys
import tarfile
import time
from pathlib import Path

import GPUtil
from loguru import logger
from numpy import mean, median


def get_avail_gpus():
    avail_gpus = GPUtil.getAvailable(order='load',
                                     limit=1,
                                     maxLoad=0.5,
                                     maxMemory=0.5,
                                     includeNan=False,
                                     excludeID=[],
                                     excludeUUID=[])
    use_gpus = ','.join([str(x) for x in avail_gpus])
    return use_gpus


def calculate_job_time(folder_path):
    cmd = shlex.split(f'./rclone lsjson -R {folder_path}')
    p = subprocess.run(cmd,
                       shell=False,
                       check=True,
                       capture_output=True,
                       text=True)
    data = json.loads(p.stdout)
    d = [x['Size'] for x in data if '.JPG' in x['Path'] and not x['IsDir']]
    num_files = len(d)
    logger.info(f'Number of files: {num_files}')
    logger.info(f'Mean size: {round(mean(d) / 1000)} KB')
    logger.info(f'Median size: {round(median(d) / 1000)} KB')
    size_in_gib = round(sum(d) / 1.074e+9, 2)
    logger.info(f'Size: {size_in_gib} GiB')
    job_time = time.strftime('%H:%M', time.gmtime(num_files + 1800))
    logger.info(f'Job time: {job_time}')
    return job_time


def to_tar(input_path):
    folder_name = Path(input_path).name
    with tarfile.open(f'{folder_name}.tar', 'w') as tar:
        tar.add(input_path, folder_name)
    logger.info(f'Archived {input_path}')


def from_tar(input_path):
    with tarfile.open(input_path) as tar:
        tar.extractall()
    logger.info(f'Extracted {input_path}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--gpus',
                        help='Get GPU names with at least 50% free memory and load',
                        action='store_true')
    parser.add_argument('--job-time',
                        type=str,
                        help='Estimate the job time based on the number of images in a specified folder')
    parser.add_argument('--c',
                        type=str,
                        help='Create a tarball')
    parser.add_argument('--x',
                        type=str,
                        help='Extract a tarball')
    args = parser.parse_args()
    
    
    if args.gpus:
        print(get_avail_gpus())

    elif args.job_time:
        if not Path(args.job_time).exists():
            raise FileNotFoundError
        print(calculate_job_time(args.job_time))

    elif args.c:
        to_tar(args.c)

    elif args.x:
        from_tar(args.x)
