#!/usr/bin/env python
# coding: utf-8

import argparse
import json
import shutil
import sys
from glob import glob
from pathlib import Path

import numpy as np
import ray
import visualize_detector_output  # noqa (from CameraTraps repo)
from loguru import logger
from ray.exceptions import RayTaskError
from tqdm import tqdm

# import random

# import ipyplot
# from tqdm.notebook import tqdm

sys.path.insert(0, f'{Path.cwd()}/CameraTraps')


def process_data(jsonfiles, update=False):
    if update or not Path('all_data.json').exists():
        logger.debug('Writing data to one file...')
        _data = []

        for json_file in jsonfiles:
            with open(json_file) as j:
                d = json.load(j)
                _data.append(d['images'])
        _data = sum(_data, [])

        with open('all_data.json', 'w') as j:
            json.dump(_data, j, indent=4)

    else:
        logger.debug('Reading from existing data file...')
        with open('all_data.json') as j:
            _data = json.load(j)
    return _data


def split_data(__data):
    _detections = []
    _no_detections = []

    for x in __data:
        if x['detections']:
            _detections.append(x)
        else:
            _no_detections.append(x)

    logger.debug(f'Detections: {len(_detections)}\nNo'
                 f'detections: {len(_no_detections)}')
    return _detections, _no_detections


def create_conf_levels_dict(_detections):
    D = {round(x, 1): [] for x in np.arange(0.1, 1, 0.1)}

    for x in tqdm(_detections):
        for k in D:
            if x['max_detection_conf'] >= k:
                D[k].append(x)

    for k in D:
        assert any([
            x['max_detection_conf'] for x in D[k]
            if x['max_detection_conf'] >= k
        ])

    logger.debug('Data size in each conf value:')
    for k, v in D.items():
        logger.debug(f'{k}: {len(v)}')
    return D


@ray.remote
def sort_files(x):
    if x['detections']:
        cat_str = 'detections'
    else:
        cat_str = 'no_detections'
    dir_path = Path(f'{cat_str}/{Path(Path(x["file"]).parent)}')
    if not Path(dir_path).exists():
        dir_path.mkdir(exist_ok=True, parents=True)
    if not Path(x['file']).exists():
        return x['file']
    shutil.copy(x["file"], f'{cat_str}/{x["file"]}')


# def sample_detections(detections,
#                       sample_size_per_level=300,
#                       output_image_width=1280):
#     random.seed(8)
#     random_D = {}
#
#     for k, v in D.items():
#         random_D.update({k: random.sample(v, sample_size_per_level)})
#
#     names = {'1': 'animal', '2': 'person', '3': 'vehicle'}
#
#     ND = random.sample([x['file'] for x in no_detections],
#                        sample_size_per_level)
#     Path('no_detections_sample').mkdir(exist_ok=True)
#     for x in ND:
#         shutil.copy2(x, f'no_detections_sample/{Path(x).name}')
#
#     for level in np.arange(0.1, 1, 0.1):
#         level = round(level, 1)
#         level_dir_path = f'levels/{level}'
#         Path(level_dir_path).mkdir(exist_ok=True, parents=True)
#
#         visualize_detector_output.visualize_detector_output(
#             detector_output_path=random_D[level],
#             out_dir=level_dir_path,
#             confidence=level,
#             images_dir='.',
#             is_azure=False,
#             sample=-1,
#             output_image_width=output_image_width,
#             random_seed=None,
#             render_detections_only=True)
#
#     display_width = output_image_width / 2
#     zoom_scale = output_image_width / display_width
#
#     levels_folders = glob(f'levels/*')
#
#     images = [glob(f'{level}/*') for level in levels_folders]
#     labels = [[Path(Path(x).parent).name for x in y] for y in images]
#
#     plot = ipyplot.plot_class_tabs(images,
#                                    labels,
#                                    max_imgs_per_tab=sample_size_per_level,
#                                    img_width=display_width,
#                                    zoom_scale=zoom_scale,
#                                    hide_images_url=False,
#                                    display=False)
#
#     with open('random_detections_sample.html', 'w') as f:
#         f.write(plot)
#     logger.info('Exported sample to `random_detections_sample.html`')


def opts():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-d',
        '--results-dir',
        type=str,
        help='Path to the results folder with the *.json files. The results '
        'directory should be in the same parent directory as the directory of '
        'the images data (e.g., `./parent/results_dir`, `./parent/images`)',
        required=True)
    parser.add_argument(
        '-c',
        '--max-detection-conf-threshold',
        type=float,
        help='Max. detection confidence threshold for detections to be kept',
        required=True)
    return parser.parse_args()


if __name__ == '__main__':
    args = opts()
    json_files = glob(f'{args.results_dir}/**/*.json', recursive=True)
    logger.debug(f'Data file path example: {json_files[0]}')

    data = process_data(json_files)
    logger.debug(f'Number of data items: {len(data)}')

    detections, no_detections = split_data(data)

    max_detection_conf = round(args.max_detection_conf, 1)
    detections = create_conf_levels_dict(detections)[max_detection_conf]

    for ITEM in [(no_detections, 'no_detections'), (detections, 'detections')]:
        futures = []
        not_found = []

        try:
            for future in tqdm(ITEM[0]):
                futures.append(sort_files.remote(future))

            for future in tqdm(futures):
                not_found.append(ray.get(future))

        except (KeyboardInterrupt, RayTaskError, TypeError) as e:
            logger.error(e)
            ray.shutdown()

        logger.debug('Number of items that were not found in'
                     f'{ITEM[1]}: {len(not_found)}')
        logger.debug('These items belong to these directories:\n'
                     f'{list(set([Path(x).parent for x in not_found]))}')

    ray.shutdown()
