#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
from __future__ import division

import os
import sys
import collections
import argparse

import cv2
import numpy as np

'''
File name convention: Txx_xxxxxxxx_xx_xxxxx_X.jpg
X: F or P
'''
TYPE_TO_CLASS = {
    # 0: background
    'T01': 1,
    'T02': 2,
    'T03': 3,
    'T05': 1,
    'T06': 3,
    'T13': 4,
    'T14': 5,
    'T17': 6,
}

THRESHOLD = 0.98

parser = argparse.ArgumentParser(description='Create annotation files (txt)')
parser.add_argument('IMAGE_DIR', help='Directory containing the images (_F and _P)')
parser.add_argument('ANNOTATION_DIR', help='Directory to save the annotations')
parser.add_argument('MATCH_DIR', help='Directory to save template match results')

def canonical_name(path):
    basename = os.path.basename(path)
    no_ext = basename.rsplit('.', 1)[0]
    return no_ext.rsplit('_', 1)[0]

def get_type(canonical_name):
    return canonical_name[:3]

def full_image_name(canonical_name):
    return '{}_F.jpg'.format(canonical_name)

def plate_image_name(canonical_name):
    return '{}_P.jpg'.format(canonical_name)

def annotation_name(canonical_name):
    return '{}_annotation.txt'.format(canonical_name)

def match_name(canonical_name):
    return '{}_match.jpg'.format(canonical_name)

if __name__ == '__main__':
    args = parser.parse_args()
    image_dir = args.IMAGE_DIR
    annotation_dir = args.ANNOTATION_DIR
    match_dir = args.MATCH_DIR

    if not os.path.exists(image_dir) or not os.path.isdir(image_dir):
        raise ValueError('Given image directory is not valid')

    if not os.path.exists(annotation_dir):
        os.makedirs(annotation_dir)

    if not os.path.exists(match_dir):
        os.makedirs(match_dir)

    all_files = os.listdir(image_dir)
    canonical_names = set(canonical_name(x) for x in all_files)

    for cn in canonical_names:
        print('Processing {}...'.format(cn), end=' ')
        f_path = os.path.join(image_dir, full_image_name(cn))
        p_path = os.path.join(image_dir, plate_image_name(cn))

        if not os.path.exists(f_path):
            print('Full image does not exist')
            sys.stdout.flush()
            continue

        if not os.path.exists(p_path):
            print('Plate image does not exist')
            sys.stdout.flush()
            continue

        f_img = cv2.imread(f_path, cv2.IMREAD_COLOR)
        p_img = cv2.imread(p_path, cv2.IMREAD_COLOR)

        #print('{} {} {} {}'.format(f_img.shape, f_img.dtype, p_img.shape, p_img.dtype), end=' ')
        match_result = cv2.matchTemplate(f_img, p_img, cv2.TM_CCOEFF_NORMED)
        _, val, _, loc = cv2.minMaxLoc(match_result)

        if val < THRESHOLD:
            print('Match value is low ({:.2f} < {:.2f})'.format(val, THRESHOLD))
            sys.stdout.flush()
            continue

        x, y = loc
        h, w = p_img.shape[:2]
        xmin, xmax, ymin, ymax = x, x+w-1, y, y+h-1
        matched = f_img[ymin:ymax+1, xmin:xmax+1]


        # Check whether template match is successful

        cls = TYPE_TO_CLASS[get_type(cn)]
        with open(os.path.join(annotation_dir, annotation_name(cn)), 'w') as annotation_file:
            print('{} {} {} {} {}'.format(cls, xmin, ymin, xmax, ymax), file=annotation_file)
        #cv2.imwrite(os.path.join(match_dir, match_name(cn)), matched)
        print('Done')
        sys.stdout.flush()
