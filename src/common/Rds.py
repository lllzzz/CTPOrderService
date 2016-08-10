#!/usr/bin/env python
# -*- encoding:utf-8 -*-

from redis import Redis
from C import C

class Rds():
    """Redis封装"""
    def __init__(self, host, port, db):
        self.rds = Redis(host = host, port = port, db = db)

    @staticmethod
    def getLocal():
        return Rds('127.0.0.1', 6379, 1)

    @staticmethod
    def getRds():
        env = C.get('sys', 'env')
        host = C.get('redis_' + env, 'host')
        db = C.get('redis_' + env, 'db')
        return Rds(host, 6379, db)

    @staticmethod
    def getSender():
        obj = Rds.getRds()
        return obj

    @staticmethod
    def getService():
        obj = Rds.getRds()
        return obj.pubsub()
