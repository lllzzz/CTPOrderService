#!/usr/bin/env python
# -*- encoding:utf-8 -*-

import sys
sys.path.append('../src/common')

from Rds import Rds
from C import C
import demjson as JSON
import time

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

            elif type == 0: # NORMAL
                # # case1 直接分批返回
                # time.sleep(1)
                # for i in range(data['total']):
                #     time.sleep(1)
                #     rspData = {
                #         'type': 'traded',
                #         'iid': data['iid'],
                #         'orderID': data['orderID'],
                #         'realPrice': data['price'],
                #         'successVol': 1,
                #     }
                #     rds.publish(rspCh, JSON.encode(rspData))
                # # case1 end

                # case2 不做处理，等待撤单
                # case2 end
                pass

        elif act == 'cancel':
            rspData = {
                'type': 'canceled',
                'orderID': data['orderID'],
                'cancelVol': 3,
            }
            rds.publish(rspCh, JSON.encode(rspData))





