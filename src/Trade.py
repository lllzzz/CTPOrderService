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

        # 初始化
        self.__initDB()
        self.__initOrderID()


    def __initDB(self):
        sql = '''
            CREATE TABLE IF NOT EXISTS `order` (
                `id` int(11) NOT NULL AUTO_INCREMENT,
                `appKey` varchar(50) NOT NULL DEFAULT '',
                `order_id` int(11) NOT NULL DEFAULT '0',
                `iid` varchar(50) NOT NULL DEFAULT '',
                `price` decimal(10,2) NOT NULL DEFAULT '0.00',
                `real_mean_price` decimal(10,2) NOT NULL DEFAULT '0.00',
                `total` int(11) NOT NULL DEFAULT 0,
                `real_total` int(11) NOT NULL DEFAULT 0,
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
                `type` int(11) NOT NULL DEFAULT '0',
                `mtime` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                PRIMARY KEY (`id`),
                KEY `idx_key_oid` (`appKey`,`order_id`)
            ) ENGINE=InnoDB CHARSET=utf8;'''
        self.db.insert(sql)


    def __initOrderID(self):
        sql = '''SELECT COALESCE(MAX(`order_id`), 0) AS 'maxOrderID' FROM `order` WHERE `appKey` = '%s' ''' % (self.appKey)
        hasData, res = self.db.getOne(sql)
        maxOrderID = res[0]
        self.localRds.set('ORDER_ID_' + self.appKey, str(maxOrderID))


    def process(self, channel, data):
        type = data['type']
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


