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

orderCh = C.get('channel', 'send_order')
rspCh = C.get('channel', 'listen_trade')
srv.subscribe(orderCh)

num = 0

for msg in srv.listen():
    if msg['type'] == 'message':
        data = msg['data']
        data = JSON.decode(data)
        print data
        act = data['action']
        appKey = data['appKey']
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
                    rspData = {'data': rspData, 'err': 0, 'msg': 'ok'}
                    rds.publish(rspCh % (appKey), JSON.encode(rspData))
                    rspData = {
                        'type': 'canceled',
                        'iid': data['iid'],
                        'orderID': data['orderID'],
                        'price': data['price'],
                        'cancelVol': 1,
                    }
                    rspData = {'data': rspData, 'err': 0, 'msg': 'ok'}
                    rds.publish(rspCh % (appKey), JSON.encode(rspData))
                else: # FAK平仓测试，成1
                    rspData = {
                        'type': 'traded',
                        'iid': data['iid'],
                        'orderID': data['orderID'],
                        'realPrice': data['price'],
                        'successVol': 1,
                    }
                    rspData = {'data': rspData, 'err': 0, 'msg': 'ok'}
                    rds.publish(rspCh % (appKey), JSON.encode(rspData))
                    rspData = {
                        'type': 'canceled',
                        'iid': data['iid'],
                        'orderID': data['orderID'],
                        'price': data['price'],
                        'cancelVol': data['total'] - 1,
                    }
                    rspData = {'data': rspData, 'err': 0, 'msg': 'ok'}
                    rds.publish(rspCh % (appKey), JSON.encode(rspData))

            elif type == 2: # IOC
                rspData = {
                    'type': 'traded',
                    'iid': data['iid'],
                    'orderID': data['orderID'],
                    'realPrice': data['price'],
                    'successVol': data['total'],
                }
                rspData = {'data': rspData, 'err': 0, 'msg': 'ok'}
                rds.publish(rspCh % (appKey), JSON.encode(rspData))

            elif type == 0: # NORMAL
                if num % 2 == 0 :
                    # case1 直接分批返回
                    time.sleep(1)
                    for i in range(data['total']):
                        time.sleep(1)
                        rspData = {
                            'type': 'traded',
                            'iid': data['iid'],
                            'orderID': data['orderID'],
                            'realPrice': data['price'],
                            'successVol': 1,
                        }
                        rspData = {'data': rspData, 'err': 0, 'msg': 'ok'}
                        rds.publish(rspCh % (appKey), JSON.encode(rspData))
                    # case1 end
                num += 1
                # case2 不做处理，等待撤单
                # case2 end
                pass

        elif act == 'cancel':
            rspData = {
                'type': 'canceled',
                'orderID': data['orderID'],
                'cancelVol': 7,
            }
            rspData = {'data': rspData, 'err': 0, 'msg': 'ok'}
            rds.publish(rspCh % (appKey), JSON.encode(rspData))





