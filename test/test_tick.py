#!/usr/bin/env python
# -*- encoding:utf-8 -*-

import sys
sys.path.append('../src/common')

from Rds import Rds
from C import C
import demjson as JSON

rds = Rds.getLocal()

ch = C.get('channel', 'tick') + 'ni1609'

tickData = {
    'price': int(sys.argv[1]),
}
rds.publish(ch, JSON.encode(tickData))
