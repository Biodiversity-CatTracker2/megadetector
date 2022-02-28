import json
import sys
from pathlib import Path

import GPUtil
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
    hrs = round(((num_files / 1000) * 15) / 60)
    job_time = str(hrs).zfill(2) + ':00'
    logger.info(f'Job time: {job_time}')
    return job_time


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
