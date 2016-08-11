#!/usr/bin/env python
# -*- encoding:utf-8 -*-

import sys
sys.path.append('../src/common')
sys.path.append('../src/orders')

from Logger import Logger
from Rds import Rds
from DB import DB

from OrderRealOpen import OrderRealOpen

class Trade():
    """交易逻辑"""

    # 预测单
    # 定义：提前下单，等待成交或者撤单信号，对于多手，成交一次以后撤掉剩下全部订单
    ORDER_TYPE_FORECAST = 0

    # 实时单
    # 定义：实时下单开仓，下FAK单
    ORDER_TYPE_REAL_OPEN = 1
    # 定义：实时下单平仓，下FAK单，尝试n次以后，下IOC单
    ORDER_TYPE_REAL_CLOSE = 2

    # 强平单
    # 定义：下IOC单
    ORDER_TYPE_IOC_CLOSE = 3


    def __init__(self, appKey):
        self.appKey = appKey
        self.logger = Logger()

        self.db = DB()
        self.localRds = Rds.getLocal()
        self.rds = Rds.getRds()

        self.iids = []
        # 初始化
        self.__initOrderID()

    def __initOrderID(self):
        sql = '''SELECT COALESCE(MAX(`order_id`), 0) AS 'maxOrderID' FROM `order_log` WHERE `appKey` = '%s' ''' % (self.appKey)
        hasData, res = self.db.getOne(sql)
        maxOrderID = res[0]
        self.localRds.set('ORDER_ID_' + self.appKey, str(maxOrderID))

    def __initVol(self, iid):
        self.rds.set('TRADING_NUM_' + self.appKey + '_' + iid, 0)


    def process(self, channel, data):
        type = data['type']
        iid = data['iid']
        if self.iids.count(iid) == 0:
            self.iids.append(iid)
            self.__initVol(iid)

        if type == self.ORDER_TYPE_FORECAST:
            order = OrderForecast(self.appKey, data)
            order.start()
        elif type == self.ORDER_TYPE_REAL_OPEN:
            order = OrderRealOpen(self.appKey, data)
            order.start()
        elif type == self.ORDER_TYPE_REAL_CLOSE:
            order = OrderRealClose(self.appKey, data)
            order.start()
        elif type == self.ORDER_TYPE_IOC_CLOSE:
            order = OrderIOCClose(self.appKey, data)
            order.start()


