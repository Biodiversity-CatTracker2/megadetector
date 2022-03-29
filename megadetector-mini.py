import argparse
import json
import os
import sys
from datetime import datetime
from glob import glob
from pathlib import Path

import tensorflow as tf
from loguru import logger
from tqdm import tqdm

sys.path.insert(0, f'{os.getcwd()}/ai4eutils')
sys.path.insert(0, f'{os.getcwd()}/CameraTraps')

try:
    from CameraTraps.detection import run_tf_detector_batch  # noqa
    from CameraTraps.visualization import visualize_detector_output  # noqa
except RuntimeError:
    print('RuntimeError')
    sys.exit(0)


class GPUNotAvailable(Exception):
    pass


def setup_dirs(images_dir):
    img_extensions = ['.jpg', '.jpeg', '.png', '.JPG', '.JPEG', '.PNG']
    images_list = sum([glob(f'{images_dir}/*{ext}') for ext in img_extensions],
                      [])
    images_list_len = len(images_list)
    if not images_list_len:
        sys.exit(
            f'No images in the current directory: {images_dir} (subdirs are '
            f'not included)')
    logger.info(f'Number of images in the folder: {images_list_len}')

    logger.info(f'Will process {len(images_list)} images')
    logger.debug(f'Images directory: {images_dir}')

    output_folder = f'{images_dir}/output'
    Path(output_folder).mkdir(exist_ok=True)
    output_file_path = output_folder + f'/data_{Path(images_dir).parent}_{Path(images_dir).name}.json'
    return images_list, output_folder, output_file_path


def main(images_dir, _restored_results):
    logger.debug(tf.__version__)
    logger.debug(f'GPU available: {tf.test.is_gpu_available()}')

    if not tf.test.is_gpu_available():
        if not args.CPU:
            raise GPUNotAvailable(
                f'No available GPUs. Terminating... Folder of terminated job:'
                f'{images_dir} ')

    images_list, output_folder, output_file_path = setup_dirs(images_dir)
    logger.info(f'Number of images in folder: {len(images_list)}')

    results = run_tf_detector_batch.load_and_run_detector_batch(
        model_file='megadetector_v4_1_0.pb',
        image_file_names=images_list,
        checkpoint_path=ckpt_path,
        confidence_threshold=0.1,
        checkpoint_frequency=100,
        results=_restored_results,
        n_cores=0,
        use_image_queue=False)

    logger.debug(
        'Finished running `run_tf_detector_batch.load_and_run_detector_batch`')

    run_tf_detector_batch.write_results_to_file(results,
                                                output_file_path,
                                                relative_path_base=None)

    logger.debug(
        'Finished running `run_tf_detector_batch.write_results_to_file`')

    logger.info(f'Data file path: {output_file_path}')

    Path(f'{images_dir}/output/_complete').touch()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--images-dir',
                        type=str,
                        help='Path to the source images folder (local)',
                        required=True)
    parser.add_argument('--resume',
                        action='store_true',
                        help='Resume from the last checkpoint')
    parser.add_argument('--animal-only',
                        help='Only filter animal detections',
                        action='store_true')
    parser.add_argument('--jobid', help='Job id')
    parser.add_argument('--CPU',
                        action='store_true',
                        help='Use CPU if GPU not available')
    parser.add_argument('--ckpt',
                        help='Path to checkpoint file other than default')
    args = parser.parse_args()

    _FOLDERS = [x for x in glob(f'{args.images_dir}/*') if Path(x).is_dir()]
    if len(_FOLDERS) > 1:
        logger.debug('Detected multiple subdirs! Running a loop...')
    else:
        _FOLDERS = [args.images_dir]

    n = 0
    for _FOLDER in tqdm(_FOLDERS):
        logger.info(f'Job id: {args.jobid}')

        if len(_FOLDERS) == 1:
            logger.add(f'logs/{args.jobid}.log')
        else:
            logger.add(f'logs/{args.jobid}_{n}.log')
            ts = datetime.now().strftime('%Y%m%d_%H%M%S')
            n += 1

        if Path(f'{_FOLDER}/output/_complete').exists():
            raise Exception('Folder already completed!')

        try:
            logger.debug(f'Images directory: {_FOLDER}')
            assert Path(
                _FOLDER).exists(), 'Specified images path does not exist'
        except AssertionError as err:
            logger.exception(err)
            sys.exit(1)

        ckpt_path = f'{_FOLDER}/output/ckpt.json'

        if args.resume:
            logger.info('Resuming from checkpoint...')
            try:
                if Path(ckpt_path).exists():
                    if args.ckpt:
                        ckpt_path = args.ckpt
                        logger.info(
                            'Resuming from custom checkpoint path instead'
                            ' of default...')
                    with open(ckpt_path) as f:
                        saved = json.load(f)

                    assert 'images' in saved, \
                        'The file saved as checkpoint does not have the ' \
                        'correct fields; cannot be restored'

                    restored_results = saved['images']
                    logger.info(f'Restored {len(restored_results)} '
                                f'entries from the checkpoint')
            except AssertionError as err:
                logger.exception(err)
                sys.exit(1)
        else:
            logger.info('Processing from the start...')
            restored_results = []

        if not args.ckpt:
            restored_results = []

        main(_FOLDER, restored_results)  # noqa
