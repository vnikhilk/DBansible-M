#!/usr/bin/python

import sys
import json
from collections import defaultdict

args = open(sys.argv[1])
json_data = json.load(args)

d = defaultdict(list)
for data in json_data:
    group = data['filesystem']
    disks = {'asmlabel': data['label']}
    d[group].append(disks)

print(dict(d))
