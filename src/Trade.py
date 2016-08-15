#!/usr/bin/env python
# -*- encoding:utf-8 -*-

import sys
sys.path.append('../src/common')
sys.path.append('../src/orders')

from Logger import Logger
from Rds import Rds
from DB import DB

from OrderRealOpen import OrderRealOpen
from OrderIOCClose import OrderIOCClose
from OrderRealClose import OrderRealClose
from OrderForecastOpen import OrderForecastOpen

class Trade():
    """交易逻辑"""

    # 预测单
    # 定义：提前下单，等待成交或者撤单信号，对于多手，成交一次以后撤掉剩下全部订单
    ORDER_TYPE_FORECAST_OPEN = 0
    ORDER_TYPE_FORECAST_CLOSE = 6
    # 定义：预测平开单
    ORDER_TYPE_FORECAST_CLOSEOPEN = 5

    # 实时单
    # 定义：实时下单开仓，下FAK单
    ORDER_TYPE_REAL_OPEN = 1
    # 定义：实时下单平仓，下FAK单，尝试n次以后，下IOC单
    ORDER_TYPE_REAL_CLOSE = 2

    # 强平单
    # 定义：下IOC单
    ORDER_TYPE_IOC_CLOSE = 3

    # 平开类型单
    # 定义：实时平开单
    ORDER_TYPE_REAL_CLOSEOPEN = 4


    def __init__(self, appKey):
        self.appKey = appKey
        self.logger = Logger()

        self.db = DB()
        self.localRds = Rds.getLocal()
        self.rds = Rds.getRds()

        self.iids = []
        # 初始化
        self.__initDB()
        self.__initOrderID()

    def __initOrderID(self):
        sql = '''SELECT COALESCE(MAX(`order_id`), 0) AS 'maxOrderID' FROM `order_log` WHERE `appKey` = '%s' ''' % (self.appKey)
        hasData, res = self.db.getOne(sql)
        maxOrderID = res[0]
        self.localRds.set('ORDER_ID_' + self.appKey, str(maxOrderID))

    def __initVol(self, iid):
        self.rds.set('TRADING_NUM_' + self.appKey + '_' + iid, 0)
        self.rds.set('BUY_VOL_' + self.appKey + '_' + iid, 0)
        self.rds.set('SELL_VOL_' + self.appKey + '_' + iid, 0)


    def process(self, channel, data):
        type = data['type']
        iid = data['iid']
        if self.iids.count(iid) == 0:
            self.iids.append(iid)
            self.__initVol(iid)

        if type == self.ORDER_TYPE_FORECAST_OPEN:
            order = OrderForecastOpen(self.appKey, data)
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

    def __initDB(self):
        sql = '''
            CREATE TABLE IF NOT EXISTS `order` (
                `id` int(11) NOT NULL AUTO_INCREMENT,
                `appKey` varchar(50) NOT NULL DEFAULT '',
                `iid` varchar(50) NOT NULL DEFAULT '',
                `order_ids` varchar(500) NOT NULL DEFAULT '',
                `type` int(11) NOT NULL DEFAULT '0',
                `price` decimal(10,2) NOT NULL DEFAULT '0.00',
                `price_mean` decimal(10,2) NOT NULL DEFAULT '0.00',
                `total` int(11) NOT NULL DEFAULT 0,
                `total_success` int(11) NOT NULL DEFAULT 0,
                `total_cancel` int(11) NOT NULL DEFAULT 0,
                `is_buy` int(1) NOT NULL DEFAULT '-1',
                `is_open` int(11) NOT NULL DEFAULT '-1',
                `srv_first_time` datetime NOT NULL COMMENT '服务器返回时间',
                `srv_end_time` datetime NOT NULL COMMENT '服务器返回时间',
                `local_start_time` datetime NOT NULL COMMENT '发出交易指令时间',
                `local_start_usec` int(11) NOT NULL DEFAULT '0',
                `local_first_time` datetime NOT NULL COMMENT '发出交易指令时间',
                `local_first_usec` int(11) NOT NULL DEFAULT '0',
                `local_end_time` datetime NOT NULL COMMENT '发出交易指令时间',
                `local_end_usec` int(11) NOT NULL DEFAULT '0',
                `mtime` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                PRIMARY KEY (`id`)
            ) ENGINE=InnoDB CHARSET=utf8;'''
        db = DB()
        db.insert(sql)
