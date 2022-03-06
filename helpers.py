import json
import shlex
import subprocess
import sys
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
    p = subprocess.run(cmd, shell=False, check=True, capture_output=True, text=True)
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


def check_progress(folder_path):
    complete_folders = []
    files = fd.find('_complete', path=folder_path)
    for file in files:
        complete_folders.append(file.split('output')[0][:-1])

    print('COMPLETE')
    print(json.dumps(complete_folders, indent=4))

    all_folders = fd.find('"" --type d', path=folder_path)
    all_ = []
    for folder in all_folders:
        if len(folder.split('output')) == 1:
            all_.append(folder.split('output')[0])
        else:
            all_.append(folder.split('output')[0][:-1])

    all_ = list(set(all_))

    no_output = [x for x in all_ if x not in complete_folders]
    print('\n\nPENDING')
    print(json.dumps(no_output, indent=4))


if __name__ == '__main__':
    if '--gpus' in sys.argv:
        print(get_avail_gpus())

    if '--job-time' in sys.argv:
        try:
            if not Path(sys.argv[2]).exists():
                raise FileNotFoundError
            print(calculate_job_time(sys.argv[2]))
        except (IndexError, FileNotFoundError):
            raise Exception('Missing valid local data folder path')

    if '--check-progress' in sys.argv:
        from fdpy import fd
        assert Path(sys.argv[2]).exists(), 'Folder does not exist!'
        check_progress(sys.argv[2])
