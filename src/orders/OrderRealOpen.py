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

    def run(self):
        self.__sendOrder()
        self.service.run()

    def process(self, channel, data):
        if self.orderID != data['orderID']: return
        self.logger.write('trade_' + self.appKey, Logger.INFO, 'OrderRealOpen[process]', data)

        self.service.stop()

    def __sendOrder(self):

        self.iid   = self.req['iid']
        self.price = self.req['price']
        self.isBuy = self.req['isBuy']
        self.total = self.req['total']

        sendData = {
            'appKey': int(self.appKey),
            'orderID': int(self.orderID),
            'iid': self.iid,
            'type': self.ORDER_TYPE_FAK,
            'price': int(self.price),
            'total': int(self.total),
            'isBuy': int(self.isBuy),
            'isOpen': 1,
        }
        self.sender.publish(self.reqCh, JSON.encode(sendData))
        self.logger.write('trade_' + self.appKey, Logger.INFO, 'OrderRealOpen[sendOrder]', sendData)
