import os
import sys
from glob import glob
from pathlib import Path

from loguru import logger


def main(imgs_extension='.JPG'):
    complete, pending = [], []

    if 'gpfs_common' not in sys.argv[1]:
        sys.argv[
            1] = f'/gpfs_common/share03/{os.environ["GROUP"]}/{os.environ["USER"]}/megadetector/' + sys.argv[
                1]

    for x in glob(f'{sys.argv[1]}/*') + glob(f'{sys.argv[1]}/**/*'):
        if glob(f'{x}/*{imgs_extension}'):
            if glob(f'{x}/output'):
                if glob(f'{x}/output/_complete'):
                    complete.append(x)
                else:
                    pending.append(x)
            else:
                pending.append(x)

    if not pending:
        logger.info('All subfolders are complete!')

    with open('schedule.csh', 'w') as f:
        f.write("#!/bin/tcsh")
        for x in pending:
            job_name = x.replace(
                f'/gpfs_common/share03/{os.environ["GROUP"]}/{os.environ["USER"]}/megadetector/',
                '')
            f.write(f"""\n
    set IMAGES_DIR="{x}"
    sed -i "/#BSUB -J/c\#BSUB -J {job_name}" megadetector_job.csh;
    sed -i "/#BSUB -o/c\#BSUB -o logs/%J.out" megadetector_job.csh;
    sed -i "/#BSUB -e/c\#BSUB -e logs/%J.err" megadetector_job.csh;
    set CONFIDENCE="0.3";
    set JOB_TIME="02:00";
    sed -i "/#BSUB -W/c\#BSUB -W $JOB_TIME" megadetector_job.csh;
    bsub -env "IMAGES_DIR='$IMAGES_DIR', CONFIDENCE='$CONFIDENCE', GROUP='$GROUP', USER='$USER'" < megadetector_job.csh;
    sleep 1
    """.replace('    ', ''))
