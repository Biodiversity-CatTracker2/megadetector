import argparse
import json
import os
import shutil
import sys
import time
import traceback
from datetime import datetime
from glob import glob
from pathlib import Path

import tensorflow as tf
from loguru import logger
from tqdm import tqdm

sys.path.insert(0, f'{os.getcwd()}/ai4eutils')
sys.path.insert(0, f'{os.getcwd()}/CameraTraps')

from CameraTraps.detection import run_tf_detector_batch
from CameraTraps.visualization import visualize_detector_output


class GPUNotAvailable(Exception):
    pass


def setup_dirs(images_dir):
    img_extensions = ['.jpg', '.jpeg', '.png', '.JPG', '.JPEG', '.PNG']
    images_list = sum([glob(f'{images_dir}/*{ext}') for ext in img_extensions], [])
    images_list_len = len(images_list)
    logger.info(f'Number of images in the folder: {images_list_len}')

    if args.skip_list:
        with open(args.skip_list) as j:
            skip_list = json.load(j)
        images_list = list(set(skip_list) ^ set([Path(x).name for x in images_list]))
        images_list = [f'{images_dir}/{x}' for x in images_list]
        logger.info(f'Skipped {images_list_len - len(images_list)} image')

    logger.info(f'Will process {len(images_list)} images')
    logger.debug(f'Images directory: {images_dir}')
    
    output_folder = f'{images_dir}/output'
    visualization_dir = f'{output_folder}/tmp'
    Path(output_folder).mkdir(exist_ok=True)
    Path(visualization_dir).mkdir(exist_ok=True)
    for subf in ['no_detections', 'with_detections_and_bb', 'with_detections']:
        Path(f'{output_folder}/{subf}').mkdir(exist_ok=True)
    output_file_path = output_folder + f'/data_{ts}.json'
    return images_list, output_folder, visualization_dir, output_file_path


def filter_output(data, output_folder, visualization_dir, images_dir):
    if args.animal_only:
        logger.info('--animal-only mode is TRUE')

    for image in tqdm(data['images']):
        if not image['detections']:
            out_path_nd = f'{output_folder}/no_detections/{Path(image["file"]).name}'
            shutil.copy2(image['file'], out_path_nd)

        else:
            if args.animal_only:
                files = []
                for detection in image['detections']:
                    if detection['category'] == '1':
                        files.append(str(Path(image["file"])))
            else:
                files = [image['file']]

            for file in files:
                img_file = visualization_dir + '/anno_' + images_dir.replace(
                    '/', '~') + '~' + Path(file).name
                out_path_with_bb = f'{images_dir}/output/with_detections_and_bb/{Path(img_file).name}'
                shutil.copy2(img_file, out_path_with_bb)
                out_path_wd = f'{images_dir}/output/with_detections/{Path(file).name}'
                shutil.copy2(file, out_path_wd)

    return f"{output_folder}/no_detections", f"{output_folder}/with_detections"


def main(images_dir, confidence, restored_results):
    logger.debug(tf.__version__)
    logger.debug(f'GPU available: {tf.test.is_gpu_available()}')

    if not tf.test.is_gpu_available():
        raise GPUNotAvailable(f'No available GPUs. Terminating... Folder of terminated job: {images_dir}')

    images_list, output_folder, visualization_dir, output_file_path = setup_dirs(
        images_dir)
    logger.info(f'Number of images in folder: {len(images_list)}')

    results = run_tf_detector_batch.load_and_run_detector_batch(
        model_file='megadetector_v4_1_0.pb',
        image_file_names=images_list,
        checkpoint_path=args.resume,
        confidence_threshold=confidence,
        checkpoint_frequency=100,
        results=restored_results,
        n_cores=0,
        use_image_queue=False)

    logger.debug(
        'Finished running `run_tf_detector_batch.load_and_run_detector_batch`')

    run_tf_detector_batch.write_results_to_file(results,
                                                output_file_path,
                                                relative_path_base=None)

    logger.debug(
        'Finished running `run_tf_detector_batch.write_results_to_file`')

    visualize_detector_output.visualize_detector_output(
        detector_output_path=output_file_path,
        out_dir=f'{output_folder}/tmp',
        confidence=confidence,
        images_dir=images_dir,
        is_azure=False,
        sample=-1,
        output_image_width=700,
        random_seed=None,
        render_detections_only=False)

    logger.debug(
        'Finished running `visualize_detector_output.visualize_detector_output`'
    )

    with open(output_file_path) as j:
        data = json.load(j)

    out_folder_nd, out_folder_wd = filter_output(data, output_folder,
                                                 visualization_dir, images_dir)

    logger.debug('Finished running `filter_output`')
    len_nd = len(glob(f"{output_folder}/no_detections/*"))
    len_wd = len(glob(f"{output_folder}/with_detections/*"))

    logger.info(f'Number of images with no detections: {len_nd}')
    logger.info(f'Number of images with detections: {len_wd}')
    logger.info(f'Data file path: {output_file_path}')


if __name__ == '__main__':
    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    logger.add(f'logs/logs_{ts}.log')
    parser = argparse.ArgumentParser()
    parser.add_argument('--images-dir', type=str, help='Path to the source images folder (local)', required=True)
    parser.add_argument('--confidence', help='Confidence threshold', required=True)
    parser.add_argument('--resume', help='Resume from last checkpoint')
    parser.add_argument('--animal-only', help='Only filter animal detections', default=False, action='store_true')
    parser.add_argument('--skip-list', help='Path to the skip list file')
    args = parser.parse_args()
    
    try:
        logger.debug(f'Images directory: {args.images_dir}')
        assert Path(args.images_dir).exists(
        ), 'Specified images path does not exist'
        assert isinstance(
            float(args.confidence),
            float), 'Confidence threshold needs to be a decimal number'
    except AssertionError as err:
        logger.exception(err)
        sys.exit(1)

    if args.resume:
        try:
            assert Path(args.resume).exists(
            ), f'Could not find a checkpoint file {args.resume}'

            with open(args.resume) as f:
                saved = json.load(f)

            assert 'images' in saved, \
                'The file saved as checkpoint does not have the correct fields; cannot be restored'

            restored_results = saved['images']
            logger.info(
                f'Restored {len(restored_results)} entries from the checkpoint'
            )
        except AssertionError as err:
            logger.exception(err)
            sys.exit(1)
    else:
        args.resume = f'{args.images_dir}/output/checkpoint_{ts}.json'
        restored_results = []

    main(args.images_dir, float(args.confidence), restored_results)
