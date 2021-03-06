#!/usr/bin/env python2

# Copyright (c) 2017-present, Facebook, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
##############################################################################

"""Perform inference on a single image or all images with a certain extension
(e.g., .jpg) in a folder.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from collections import defaultdict
import argparse
import cv2  # NOQA (Must import before importing caffe2 due to bug in cv2)
import glob
import logging
import os
import sys
import time

from caffe2.python import workspace

from detectron.core.config import assert_and_infer_cfg
from detectron.core.config import cfg
from detectron.core.config import merge_cfg_from_file
from detectron.utils.io import cache_url
from detectron.utils.logging import setup_logging
from detectron.utils.timer import Timer
import detectron.core.test_engine as infer_engine
import detectron.datasets.dummy_datasets as dummy_datasets
import detectron.utils.c2 as c2_utils
import detectron.utils.vis as vis_utils

c2_utils.import_detectron_ops()

# OpenCL may be enabled by default in OpenCV3; disable it because it's not
# thread safe and causes unwanted GPU memory allocations.
cv2.ocl.setUseOpenCL(False)


def parse_args():
    parser = argparse.ArgumentParser(description='End-to-end inference')
    parser.add_argument(
        '--cfg',
        dest='cfg',
        help='cfg model file (/path/to/model_config.yaml)',
        default=None,
        type=str
    )
    parser.add_argument(
        '--wts',
        dest='weights',
        help='weights model file (/path/to/model_weights.pkl)',
        default=None,
        type=str
    )
    parser.add_argument(
        '--output-dir',
        dest='output_dir',
        help='directory for visualization pdfs (default: /tmp/infer_simple)',
        default='/tmp/infer_simple',
        type=str
    )
    parser.add_argument(
        '--image-ext',
        dest='image_ext',
        help='image file name extension (default: jpg)',
        default='jpg',
        type=str
    )
    parser.add_argument(
        'im_or_folder', help='image or folder of images', default=None
    )
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)
    return parser.parse_args()


def main(args):
    logger = logging.getLogger(__name__)
    merge_cfg_from_file(args.cfg)
    cfg.NUM_GPUS = 1
    args.weights = cache_url(args.weights, cfg.DOWNLOAD_CACHE)
    assert_and_infer_cfg(cache_urls=False)
    model = infer_engine.initialize_model_from_cfg(args.weights)
    dummy_coco_dataset = dummy_datasets.get_coco_dataset()

    # if os.path.isdir(args.im_or_folder):
        # im_list = glob.iglob(args.im_or_folder + '/*.' + args.image_ext)
    # else:
        # im_list = [args.im_or_folder]

    for fold in os.listdir(args.im_or_folder):
        _fold = os.path.join(args.im_or_folder, fold)
        if os.path.isdir(_fold):
            im_list = glob.iglob(_fold + '/*.' + args.image_ext)
        else:
            im_list = [args.im_or_folder]
        output_dir = os.path.join(args.output_dir, fold)
        if not os.path.exists(output_dir):
            os.mkdir(output_dir)
        for i, im_name in enumerate(im_list):
            out_name = os.path.join(
                output_dir, '{}'.format(os.path.basename(im_name) + '.pdf')
            )
            logger.info('Processing {} -> {}'.format(im_name, out_name))
            im = cv2.imread(im_name)
            timers = defaultdict(Timer)
            t = time.time()
            with c2_utils.NamedCudaScope(0):
                cls_boxes, cls_segms, cls_keyps = infer_engine.im_detect_all(
                    model, im, None, timers=timers
                )
            logger.info('Inference time: {:.3f}s'.format(time.time() - t))
            for k, v in timers.items():
                logger.info(' | {}: {:.3f}s'.format(k, v.average_time))
            if i == 0:
                logger.info(
                    ' \ Note: inference on the first image will be slower than the '
                    'rest (caches and auto-tuning need to warm up)'
                )

            vis_utils.vis_one_image(
                im[:, :, ::-1],  # BGR -> RGB for visualization
                im_name[:-4],
                output_dir,
                cls_boxes,
                cls_segms,
                cls_keyps,
                dataset=dummy_coco_dataset,
                box_alpha=0.3,
                show_class=True,
                thresh=0.7,
                kp_thresh=2,
		ext='jpg'
            )

	    import pycocotools.mask as mask_util
	    boxes, segms, keypoints, classes = vis_utils.convert_from_cls_format(cls_boxes, cls_segms, cls_keyps)
	    if segms is not None and len(segms) > 0: 
	       score = boxes[:, -1]
	       index = [i for i,_sc in enumerate(score) if _sc > 0.7]
	       mask = mask_util.decode(segms)
	       for i in index:
	          cv2.imwrite('{}/{}_{}.jpg'.format(output_dir, im_name.split('/')[-1][:-4], i), mask[:,:,i] * 255.0)
	    


if __name__ == '__main__':
    workspace.GlobalInit(['caffe2', '--caffe2_log_level=0'])
    setup_logging(__name__)
    args = parse_args()
    main(args)
