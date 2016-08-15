#!/usr/bin/env python
# -*- encoding:utf-8 -*-
import sys
sys.path.append('../common')

from Base import Base
import demjson as JSON
from Logger import Logger

class OrderRealOpen(Base):
    """实时开仓单：直接下FAK单"""
    def __init__(self, appKey, req):
        Base.__init__(self, appKey, req)
        self.selfCh = C.get('channel', 'trade_rsp') + appKey


    def run(self):
        self.__sendOrder()
        self.service.run()

    def process(self, channel, data):
        if channel != self.selfCh: return
        if self.orderID != data['orderID']: return
        data['volWaiting'] = self.total
        self.logger.write('trade_' + self.appKey, Logger.INFO, 'OrderRealOpen[process]', data)

        isOver = False
        type = data['type']
        if type == 'traded':
            vol = data['successVol']
            # 更新持仓
            if self.isBuy:
                self.buyVol(self.iid, vol, True)
            else:
                self.sellVol(self.iid, vol, True)

            # 判断是否结束
            self.total -= vol
            if self.total == 0:
                isOver = True

        elif type == 'canceled':
            vol = data['cancelVol']
            self.total -= vol
            if self.total == 0:
                isOver = True

        if isOver:
            self.endOrder(self.iid)
            self.toDB()
            self.service.stop()

    def __sendOrder(self):

        self.iid   = self.req['iid']
        self.price = self.req['price']
        self.isBuy = self.req['isBuy']
        self.isOpen = 1
        self.total = self.req['total']
        self.totalOri = self.total
        self.type = 1
        orderID = self.getOrderID()

        sendData = {
            'action': 'trade',
            'appKey': int(self.appKey),
            'orderID': int(orderID),
            'iid': self.iid,
            'type': self.ORDER_TYPE_FAK,
            'price': int(self.price),
            'total': int(self.total),
            'isBuy': int(self.isBuy),
            'isOpen': 1,
        }
        self.startOrder(self.iid)
        self.sender.publish(self.reqCh, JSON.encode(sendData))
        self.logger.write('trade_' + self.appKey, Logger.INFO, 'OrderRealOpen[sendOrder]', sendData)
