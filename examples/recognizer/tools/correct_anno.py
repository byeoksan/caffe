#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function

import sys
import re

import caffe
from google.protobuf import text_format

LABELS_MAP = 'labels_map.prototxt'

annofile = sys.argv[1]

with open(annofile, 'r') as f:
    lines = f.readlines()

names, bboxes = zip(*[line.split(None, 1) for line in lines])
names = (re.sub(r'T..-', '', name) for name in names)

name_label_map = {}
m = caffe.proto.caffe_pb2.LabelMap()

with open(LABELS_MAP, 'r') as f:
    text_format.Merge(str(f.read()), m)

for item in m.item:
    name_label_map[item.name.encode('utf-8')] = item.label

with open(annofile, 'w') as f:
    for name, bbox in zip(names, bboxes):
        print('{} {}'.format(name_label_map[name], bbox), file=f, end='')
