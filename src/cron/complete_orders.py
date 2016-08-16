#!/usr/bin/env python
# -*- encoding:utf-8 -*-

import sys
sys.path.append('../src/common')

from C import C
from DB import DB

TRADE = 1
ORDER = 2
TRADED = 3
CANCELED = 4

db = DB()
sql = '''SELECT * FROM `order` WHERE `status` = 0 '''
total, orders = db.getAll(sql)

if total > 0:
    for order in orders:
        oids = order['order_ids']
        appKey = order['appKey']
        iid = order['iid']
        sql = ''' SELECT * FROM `order_log` WHERE `appKey` = '%s' AND `iid` = '%s' AND `order_id` in (%s) ORDER BY `id` ''' % (appKey, iid, oids)
        t, logs = db.getAll(sql)
        if t > 0:
            priceMean = 0.0
            totalSuccess = 0
            totalCancel = 0
            sft = sot = ''
            lst = lft = let = ''
            lsu = lfu = leu = 0
            for l in logs:
                type = l['type']
                if type == TRADE:
                    lst = l['local_time']
                    lsu = l['local_usec']

                elif type == ORDER and sft == '':
                    sft = l['srv_time']
                    lft = l['local_time']
                    lfu = l['local_usec']

                elif type == TRADED:
                    priceMean += float(l['price'])
                    totalSuccess += 1

                elif type == CANCELED:
                    totalCancel += 1

            last = logs[-1]
            sot = last['srv_time']
            let = last['local_time']
            leu = last['local_usec']

            priceMean = priceMean / totalSuccess if totalSuccess > 0 else 0

            sql = ''' UPDATE `order` SET `price_mean` = '%s', `total_success` = '%s', `total_cancel` = '%s', status = 1, `srv_first_time` = '%s',
                `srv_end_time` = '%s', `local_start_time` = '%s', `local_start_usec` = '%s', `local_first_time` = '%s', `local_first_usec` = '%s',
                `local_end_time` = '%s', `local_end_usec` = '%s' WHERE `appKey` = '%s' AND `iid` = '%s' AND `order_ids` = '%s' ''' % (priceMean,
                totalSuccess, totalCancel, sft, sot, lst, lsu, lft, lfu, let, leu, appKey, iid, oids)
            db.update(sql)
