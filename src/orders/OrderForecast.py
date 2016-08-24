#!/usr/bin/env python
# -*- encoding:utf-8 -*-
import sys
sys.path.append('../common')

from Base import Base
import demjson as JSON
from Logger import Logger
from C import C
import datetime


class OrderForecast(Base):
    """预测开仓单，当tick达到下单价时检查是否撤单"""
    def __init__(self, appKey, req):
        Base.__init__(self, appKey, req)
        self.startCheckCancel = False
        self.isCanceled = False

    def run(self):
        self.__sendOrder()
        self.service.run()

    def process(self, channel, data):

        if channel == self.tickCh:

            if self.__checkTime(data):
                self.__cancel(self.total)

            if self.startCheckCancel:
                if abs(self.price - data[self.checkCancelKey]) > self.cancelRange * self.minTick:
                    self.__cancel(self.total)
            else:
                if data['price'] >= self.cancelPriceH or data['price'] <= self.cancelPriceL:
                    self.startCheckCancel = True
                    self.logger.write('trade_' + self.appKey, Logger.INFO, 'OrderForecast[tick]', data)
            return

        if channel == self.tradeRspCh:
            if data['err'] > 0:
                self.logger.write('trade_' + self.appKey, Logger.INFO, 'OrderForecast[error]', data)
                self.error(data['err'])
                return

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
            self.sender.publish(self.sendOrderRspCh, JSON.encode({'mid': self.mid, 'successVol': self.successVol}))
            self.toDB()
            self.service.stop()


    def __sendOrder(self):

        self.mid   = self.req['mid']
        self.cancelRange = int(self.req['cancelRange'])
        self.minTick = int(C.get('min_tick', self.req['iid']))
        self.cancelPriceH = int(self.req['cancelPriceH'])
        self.cancelPriceL = int(self.req['cancelPriceL'])
        self.cancelTime = self.req['cancelTime']
        self.cancelTime = datetime.datetime.strptime(self.cancelTime, '%Y%m%d_%H:%M:%S')
        self.checkCancelKey = 'price'

        self.iid   = self.req['iid']
        self.price = self.req['price']
        self.isBuy = self.req['isBuy']
        self.isOpen = self.req['isOpen']
        self.total = self.req['total']
        self.totalOri = self.total
        self.type = 0

        if not self.isOpen:
            if self.isBuy:
                self.checkCancelKey = 'ask1'
            else:
                self.checkCancelKey = 'bid1'

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
        self.sender.publish(self.sendOrderCh, JSON.encode(sendData))
        self.logger.write('trade_' + self.appKey, Logger.INFO, 'OrderForecast[sendOrder]', sendData)


    def __cancel(self, total):
        if self.isCanceled: return
        self.isCanceled = True
        sendData = {
            'action': 'cancel',
            'appKey': int(self.appKey),
            'orderID': int(self.orderID),
        }
        self.sender.publish(self.sendOrderCh, JSON.encode(sendData))
        self.logger.write('trade_' + self.appKey, Logger.INFO, 'OrderForecast[cancel]', sendData)

    def __checkTime(self, tick):
        now = datetime.datetime.strptime(tick['time'], '%Y%m%d_%H:%M:%S')
        return True if now > self.cancelTime else False
