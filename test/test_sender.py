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
ch2listen = C.get('channel', 'service_rsp') + appKey

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

elif orderType == 'Forecast':
    sendData = {
        'type': 0,
        'iid': 'ni1609',
        'total': 3,
        'isBuy': 1,
        'isOpen': 1,
        'price': 100,
        'fid': 1,
        'cancelRange': 2,
    }
rds.publish(ch, JSON.encode(sendData))

if orderType == 'Forecast':
    srv = rds.pubsub()
    srv.subscribe(ch2listen)
    for msg in srv.listen():
        if msg['type'] == 'message':
            print msg['data']

