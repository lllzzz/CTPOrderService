#!/usr/bin/env python
# -*- encoding:utf-8 -*-

import sys
sys.path.append('../src/common')

from Rds import Rds
from C import C
import demjson as JSON

rds = Rds.getLocal()

appKey = '100'
ch = C.get('channel', 'service') + appKey

sendData = {
    'type': 1,
    'price': 100,
    'iid': 'ni1609',
    'total': 2,
    'isBuy': 1,
}

rds.publish(ch, JSON.encode(sendData))

