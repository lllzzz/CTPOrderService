#!/usr/bin/env python
# -*- encoding:utf-8 -*-

import sys

from Rds import Rds
import demjson as JSON

class Service():
    """服务"""
    def __init__(self, appKey, channels, callback):
        self.appKey = appKey
        self.srv = Rds.getService()
        self.srv.subscribe(channels)
        self.callback = callback
        self.chs = channels

    def run(self):
        for msg in self.srv.listen():
            if msg['type'] == 'message':
                data = msg['data']
                if (data == 'stop'): break
                dataObj = JSON.decode(data)
                self.callback(msg['channel'], dataObj)


    def stop(self):
        sender = Rds.getSender()
        for ch in self.chs:
            sender.publish(ch, 'stop')
