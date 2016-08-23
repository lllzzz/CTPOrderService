#!/usr/bin/env python
# -*- encoding:utf-8 -*-

import sys
sys.path.append('../src/common')

from Rds import Rds
from C import C
import demjson as JSON
import time

rds = Rds.getLocal()

appKey = '100'
ch = C.get('channel', 'send_order_rsp') % (appKey)
sendCh = C.get('channel', 'listen_model') % (appKey)

rds = Rds.getLocal()
srv = rds.pubsub()
srv.subscribe(ch)

num = 1
# RealOpen
sendData = {
    'type': 1,
    'price': 100,
    'iid': 'ni1609',
    'total': 7,
    'isBuy': 1,
    'mid': num,
}
rds.publish(sendCh, JSON.encode(sendData))

for msg in srv.listen():
    if msg['type'] == 'message':
        data = msg['data']
        data = JSON.decode(data)
        print data

        vol = data['successVol']

        num += 1

        if num == 2:
            # RealClose
            sendData = {
                'type': 2,
                'price': 100,
                'iid': 'ni1609',
                'total': int(vol),
                'isBuy': 0,
                'mid': num,
            }
            rds.publish(sendCh, JSON.encode(sendData))
        elif num == 3:
            # real open
            sendData = {
                'type': 1,
                'price': 100,
                'iid': 'ni1609',
                'total': 7,
                'isBuy': 1,
                'mid': num,
            }
            rds.publish(sendCh, JSON.encode(sendData))
        elif num == 4:
            # ioc
            sendData = {
                'type': 3,
                'iid': 'ni1609',
                'total': vol,
                'isBuy': 0,
                'mid': num,
            }
            rds.publish(sendCh, JSON.encode(sendData))

        elif num == 5:
            # forecast open 分批返回
            sendData = {
                'type': 0,
                'iid': 'ni1609',
                'total': 7,
                'isBuy': 1,
                'isOpen': 1,
                'price': 100,
                'mid': num,
                'cancelRange': 2,
            }
            rds.publish(sendCh, JSON.encode(sendData))

        elif num == 6:
            # forecast close 没响应等待撤单
            sendData = {
                'type': 0,
                'iid': 'ni1609',
                'total': 7,
                'isBuy': 0,
                'isOpen': 0,
                'price': 100,
                'mid': num,
                'cancelRange': 2,
            }
            rds.publish(sendCh, JSON.encode(sendData))

            # 发送tick
            tickCh = C.get('channel', 'listen_tick') % ('ni1609')
            p = 80
            for i in range(8):
                tickData = {
                    'price': p,
                    'ask1': p + 10,
                    'bid1': p - 10,
                }
                time.sleep(1)
                p += 10
                rds.publish(tickCh, JSON.encode(tickData))

        elif num == 7:
            # forecast close 没响应等待撤单
            sendData = {
                'type': 0,
                'iid': 'ni1609',
                'total': 7,
                'isBuy': 0,
                'isOpen': 0,
                'price': 100,
                'mid': num,
                'cancelRange': 2,
            }
            rds.publish(sendCh, JSON.encode(sendData))
        elif num == 8:
            break


# orderType = sys.argv[1]
# sendData = {}
# if orderType == 'RealOpen':
#     sendData = {
#         'type': 1,
#         'price': 100,
#         'iid': 'ni1609',
#         'total': 7,
#         'isBuy': 1,
#     }
# elif orderType == 'IOCClose':
#     sendData = {
#         'type': 3,
#         'iid': 'ni1609',
#         'total': 2,
#         'isBuy': 0,
#     }
# elif orderType == 'RealClose':
#     sendData = {
#         'type': 2,
#         'iid': 'ni1609',
#         'total': 4,
#         'isBuy': 0,
#         'price': 100,
#     }

# elif orderType == 'Forecast':
#     sendData = {
#         'type': 0,
#         'iid': 'ni1609',
#         'total': 3,
#         'isBuy': 1,
#         'isOpen': 1,
#         'price': 100,
#         'fid': 1,
#         'cancelRange': 2,
#     }

# elif orderType == 'custom':
#     typeConf = {
#         'realopen': 1, 'ioc': 3, 'realclose': 2, 'forecast': 0
#     }
#     sendData = {
#         'type': typeConf[sys.argv[2]],
#         'iid': 'ni1609',
#         'total': int(sys.argv[3]),
#         'isBuy': int(sys.argv[4]),
#         'isOpen': int(sys.argv[5]),
#         'price': int(sys.argv[6]),
#         'fid': 1,
#         'cancelRange': 2,
#     }
#     if sys.argv[2] == 'forecast': orderType = 'Forecast'

# rds.publish(ch, JSON.encode(sendData))

# if orderType == 'Forecast':
#     srv = rds.pubsub()
#     srv.subscribe(ch2listen)
#     for msg in srv.listen():
#         if msg['type'] == 'message':
#             print msg['data']
#             break

