#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import collections

import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Create annotation files (txt) with given bbox text file')
    parser.add_argument('bbox', help='bbox text file')
    parser.add_argument('outdir', help='output directory to store annotation files')

    args = parser.parse_args()
    bbox = args.bbox
    outdir = args.outdir

    if not os.path.exists(outdir):
        os.makedirs(outdir)

    filename_to_bboxes = collections.defaultdict(list)
    with open(bbox, 'r') as f_bbox:
        for line in f_bbox:
            splitted = line.strip().split(' ')
            bbox = [int(x) for x in splitted[-4:]] # x, y, w, h
            bbox[2] += bbox[0] - 1 # xmax
            bbox[3] += bbox[1] - 1 # ymax
            label = int(splitted[-5])
            filename = ' '.join(splitted[:-5])

            filename_to_bboxes[filename].append((label, bbox))

    for filename, bboxes in filename_to_bboxes.items():
        outname = '{}.txt'.format(os.path.basename(filename).rsplit('.', 1)[0])
        with open(os.path.join(args.outdir, outname), 'w') as f_out:
            for bbox in bboxes:
                f_out.write('{} {} {} {} {}\n'.format(bbox[0], *bbox[1]))
