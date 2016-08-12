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
        act = data['action']
        if act == 'trade':
            type = data['type']
            if type == 1: # FAK
                if data['isOpen']: # FAK开仓测试，下单5手，成4撤1
                    rspData = {
                        'type': 'traded',
                        'iid': data['iid'],
                        'orderID': data['orderID'],
                        'realPrice': data['price'],
                        'successVol': data['total'] - 1,
                    }
                    rds.publish(rspCh, JSON.encode(rspData))
                    rspData = {
                        'type': 'canceled',
                        'iid': data['iid'],
                        'orderID': data['orderID'],
                        'price': data['price'],
                        'cancelVol': 1,
                    }
                    rds.publish(rspCh, JSON.encode(rspData))
                else: # FAK平仓测试，成1
                    rspData = {
                        'type': 'traded',
                        'iid': data['iid'],
                        'orderID': data['orderID'],
                        'realPrice': data['price'],
                        'successVol': 1,
                    }
                    rds.publish(rspCh, JSON.encode(rspData))
                    rspData = {
                        'type': 'canceled',
                        'iid': data['iid'],
                        'orderID': data['orderID'],
                        'price': data['price'],
                        'cancelVol': data['total'] - 1,
                    }
                    rds.publish(rspCh, JSON.encode(rspData))

            elif type == 2: # IOC
                rspData = {
                    'type': 'traded',
                    'iid': data['iid'],
                    'orderID': data['orderID'],
                    'realPrice': data['price'],
                    'successVol': data['total'],
                }
                rds.publish(rspCh, JSON.encode(rspData))




