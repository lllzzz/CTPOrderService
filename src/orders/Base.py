#!/usr/bin/env python
# -*- encoding:utf-8 -*-
import sys
sys.path.append('../common')

import threading
from Logger import Logger
from Service import Service
from Rds import Rds
from C import C
import demjson as JSON


class Base(threading.Thread):

    ORDER_TYPE_NORMAL = 0
    ORDER_TYPE_FAK    = 1
    ORDER_TYPE_IOC    = 2
    ORDER_TYPE_FOK    = 3

    """订单基类，每个订单为独立子线程，自动管理处理订单的行为"""
    def __init__(self, appKey, req):

        threading.Thread.__init__(self)
        self.appKey = appKey
        self.req = req

        self.logger = Logger()

        srvChannel = C.get('channel', 'trade_rsp') + appKey
        self.service = Service(appKey, [srvChannel], self.process)

        self.sender = Rds.getSender()
        self.rds = Rds.getRds()
        self.localRds = Rds.getLocal()

        self.rspCh = C.get('channel', 'service_rsp') + appKey
        self.reqCh = C.get('channel', 'trade')

        self.orderID = self.localRds.incr('ORDER_ID_' + appKey)


    def buyVol(self, iid, vol):
        if vol > 0:
            self.rds.incrby('BUY_VOL_' + self.appKey + '_' + iid, vol)
        else:
            self.rds.decrby('BUY_VOL_' + self.appKey + '_' + iid, vol)

    def sellVol(self, iid, vol):
        if vol > 0:
            self.rds.incrby('SELL_VOL_' + self.appKey + '_' + iid, vol)
        else:
            self.rds.decrby('SELL_VOL_' + self.appKey + '_' + iid, vol)


    def startOrder(self, iid):
        self.rds.incr('TRADING_NUM_' + self.appKey + '_' + iid)

    def endOrder(self, iid):
        self.rds.decr('TRADING_NUM_' + self.appKey + '_' + iid)

