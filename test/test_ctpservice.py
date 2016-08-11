#!/usr/bin/env python
# -*- encoding:utf-8 -*-

import sys
sys.path.append('../src/common')

from Rds import Rds
from C import C
import demjson as JSON

rds = Rds.getLocal()
srv = rds.pubsub()

ch = C.get('channel', 'trade')
rspCh = C.get('channel', 'trade_rsp') + '100'
srv.subscribe(ch)

for msg in srv.listen():
    if msg['type'] == 'message':
        data = msg['data']
        data = JSON.decode(data)
        print data
        rspData = {
            'type': 'traded',
            'iid': data['iid'],
            'orderID': data['orderID'],
            'realPrice': data['price'],
            'successVol': data['total'],
        }
        rds.publish(rspCh, JSON.encode(rspData))


