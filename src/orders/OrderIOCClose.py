#!/usr/bin/env python
# -*- encoding:utf-8 -*-
import sys
sys.path.append('../common')

from Base import Base
import demjson as JSON
from Logger import Logger
from C import C

class OrderIOCClose(Base):
    """IOC强平单"""
    def __init__(self, appKey, req):
        Base.__init__(self, appKey, req)
        self.selfCh = C.get('channel', 'trade_rsp') + appKey

    def run(self):
        self.__sendOrder()
        self.service.run()

    def process(self, channel, data):
        if channel != self.selfCh: return
        data = data['data']
        if self.orderID != data['orderID']: return
        data['volWaiting'] = self.total
        self.logger.write('trade_' + self.appKey, Logger.INFO, 'OrderIOCClose[process]', data)

        isOver = False
        type = data['type']
        if type == 'traded':
            vol = data['successVol']
            # 更新持仓
            if self.isBuy:
                self.sellVol(self.iid, vol, False)
            else:
                self.buyVol(self.iid, vol, False)

            # 判断是否结束
            self.total -= vol
            if self.total == 0:
                isOver = True

        if isOver:
            self.endOrder(self.iid)
            self.toDB()
            self.service.stop()

    def __sendOrder(self):

        self.iid   = self.req['iid']
        self.price = 0
        self.isBuy = self.req['isBuy']
        self.isOpen = 0
        self.total = self.req['total']
        self.totalOri = self.total
        self.type = 3
        orderID = self.getOrderID()

        sendData = {
            'action': 'trade',
            'appKey': int(self.appKey),
            'orderID': int(orderID),
            'iid': self.iid,
            'type': self.ORDER_TYPE_IOC,
            'price': 0,
            'total': int(self.total),
            'isBuy': int(self.isBuy),
            'isOpen': 0,
        }
        self.startOrder(self.iid)
        self.sender.publish(self.reqCh, JSON.encode(sendData))
        self.logger.write('trade_' + self.appKey, Logger.INFO, 'OrderIOCClose[sendOrder]', sendData)
