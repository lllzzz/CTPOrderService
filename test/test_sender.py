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

orderType = sys.argv[1]
sendData = {}
if orderType == 'RealOpen':
    sendData = {
        'type': 1,
        'price': 100,
        'iid': 'ni1609',
        'total': 7,
        'isBuy': 1,
    }
elif orderType == 'IOCClose':
    sendData = {
        'type': 3,
        'iid': 'ni1609',
        'total': 2,
        'isBuy': 0,
    }
elif orderType == 'RealClose':
    sendData = {
        'type': 2,
        'iid': 'ni1609',
        'total': 4,
        'isBuy': 0,
        'price': 100,
    }
rds.publish(ch, JSON.encode(sendData))

