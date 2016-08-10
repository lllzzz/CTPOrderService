#!/usr/bin/env python
# -*- encoding:utf-8 -*-
import MySQLdb
from C import C

class DB():

    """数据库管理类"""
    def __init__(self):

        env = C.get('sys', 'env')
        host = C.get('mysql_' + env, 'host')
        user = C.get('mysql_' + env, 'user')
        passwd = C.get('mysql_' + env, 'password')
        name = C.get('mysql_' + env, 'name')

        self.db = MySQLdb.connect(
            host = host,
            port = 3306,
            user = user,
            passwd = passwd,
            db = name,
            charset='utf8')
        self.cursor = self.db.cursor()

    def getAll(self, sql):
        self.cursor.execute(sql)
        res = self.cursor.fetchall()
        return len(res), res

    def getOne(self, sql):
        self.cursor.execute(sql)
        res = self.cursor.fetchone()
        flg = False if not res or len(res) == 0 else True
        return flg, res

    def insert(self, sql):
        self.cursor.execute(sql)
        self.db.commit()

    def update(self, sql):
        self.cursor.execute(sql)
        self.db.commit()

