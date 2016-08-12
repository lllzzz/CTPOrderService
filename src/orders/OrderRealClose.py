#!/usr/bin/env python
# -*- encoding:utf-8 -*-
import sys
sys.path.append('../common')

from Base import Base
import demjson as JSON
from Logger import Logger
from C import C

class OrderRealClose(Base):
    """实时平仓单"""
    def __init__(self, appKey, req):
        Base.__init__(self, appKey, req)

    def run(self):
        self.__sendOrder()
        self.service.run()

    def process(self, channel, data):

        if self.orderID != data['orderID']: return

        data['volWaiting'] = self.total
        self.logger.write('trade_' + self.appKey, Logger.INFO, 'OrderRealClose[process]', data)

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

        if type == 'canceled':
            if self.trytimes == 0:
                self.__sendIOC(self.total)
            else:
                price = data['price']
                price = price + self.minTick if self.isBuy else price - self.minTick
                self.__doSend(self.total, price)

        if isOver:
            self.endOrder(self.iid)
            self.toDB()
            self.service.stop()


    def __sendOrder(self):

        self.iid   = self.req['iid']
        self.price = self.req['price']
        self.isBuy = self.req['isBuy']
        self.isOpen = 0
        self.total = self.req['total']
        self.totalOri = self.total
        self.type = 2
        self.trytimes = int(C.get('sys', 'close_trytimes'))
        self.minTick = int(C.get(self.iid, 'min_tick'))

        self.startOrder(self.iid)
        self.__doSend(self.total, self.price)


    def __doSend(self, total, price):
        self.trytimes -= 1
        orderID = self.getOrderID()

        sendData = {
            'action': 'trade',
            'appKey': int(self.appKey),
            'orderID': int(orderID),
            'iid': self.iid,
            'type': self.ORDER_TYPE_FAK,
            'price': int(price),
            'total': int(total),
            'isBuy': int(self.isBuy),
            'isOpen': 0,
        }
        self.sender.publish(self.reqCh, JSON.encode(sendData))
        self.logger.write('trade_' + self.appKey, Logger.INFO, 'OrderRealClose[sendOrder]', sendData)


    def __sendIOC(self, total):
        orderID = self.getOrderID()

        sendData = {
            'action': 'trade',
            'appKey': int(self.appKey),
            'orderID': int(orderID),
            'iid': self.iid,
            'type': self.ORDER_TYPE_IOC,
            'price': 0,
            'total': int(total),
            'isBuy': int(self.isBuy),
            'isOpen': 0,
        }
        self.sender.publish(self.reqCh, JSON.encode(sendData))
        self.logger.write('trade_' + self.appKey, Logger.INFO, 'OrderRealClose[sendIOC]', sendData)
