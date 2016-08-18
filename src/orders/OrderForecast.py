#!/usr/bin/env python
# -*- encoding:utf-8 -*-
import sys
sys.path.append('../common')

from Base import Base
import demjson as JSON
from Logger import Logger
from C import C

class OrderForecast(Base):
    """预测开仓单，当tick达到下单价时检查是否撤单"""
    def __init__(self, appKey, req):
        Base.__init__(self, appKey, req)
        self.tickCh = C.get('channel', 'tick') % (req['iid'])
        self.selfCh = C.get('channel', 'trade_rsp') % (appKey)
        self.startCheckCancel = False

    def run(self):
        self.__sendOrder()
        self.service.run()

    def process(self, channel, data):

        if channel == self.tickCh:
            if self.startCheckCancel:
                if abs(self.price - data['price']) > self.cancelRange * self.minTick:
                    self.__cancel(self.total)
            else:
                if (not self.isBuy and data['price'] > self.price) or (self.isBuy and data['price'] < self.price):
                    self.startCheckCancel = True
                    self.logger.write('trade_' + self.appKey, Logger.INFO, 'OrderForecast[tick]', data)
            return

        if channel == self.selfCh:
            data = data['data']
            if self.orderID != data['orderID']: return
            data['volWaiting'] = self.total
            self.logger.write('trade_' + self.appKey, Logger.INFO, 'OrderForecast[process]', data)

            isOver = False
            type = data['type']

            if type == 'traded':
                vol = data['successVol']
                self.successVol += vol
                # 更新持仓
                if self.isBuy:
                    self.buyVol(self.iid, vol, True)
                else:
                    self.sellVol(self.iid, vol, True)

                # 判断是否结束
                self.total -= vol
                if self.total == 0:
                    isOver = True

            if type == 'canceled':
                vol = data['cancelVol']
                self.total -= vol
                if self.total == 0:
                    isOver = True

        if isOver:
            self.endOrder(self.iid)
            self.sender.publish(self.rspCh, JSON.encode({'mid': self.mid, 'successVol': self.successVol}))
            self.toDB()
            self.service.stop()


    def __sendOrder(self):

        self.mid   = self.req['mid']
        self.cancelRange = int(self.req['cancelRange'])
        self.minTick = int(C.get('min_tick', self.req['iid']))

        self.iid   = self.req['iid']
        self.price = self.req['price']
        self.isBuy = self.req['isBuy']
        self.isOpen = self.req['isOpen']
        self.total = self.req['total']
        self.totalOri = self.total
        self.type = 0

        self.startOrder(self.iid)

        orderID = self.getOrderID()
        sendData = {
            'action': 'trade',
            'appKey': int(self.appKey),
            'orderID': int(orderID),
            'iid': self.iid,
            'type': self.ORDER_TYPE_NORMAL,
            'price': int(self.price),
            'total': int(self.total),
            'isBuy': int(self.isBuy),
            'isOpen': int(self.isOpen),
        }
        self.sender.publish(self.reqCh, JSON.encode(sendData))
        self.logger.write('trade_' + self.appKey, Logger.INFO, 'OrderForecast[sendOrder]', sendData)


    def __cancel(self, total):
        sendData = {
            'action': 'cancel',
            'appKey': int(self.appKey),
            'orderID': int(self.orderID),
        }
        self.sender.publish(self.reqCh, JSON.encode(sendData))
        self.logger.write('trade_' + self.appKey, Logger.INFO, 'OrderForecast[cancel]', sendData)
