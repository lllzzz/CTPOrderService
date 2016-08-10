#!/usr/bin/env python
# -*- encoding:utf-8 -*-

from ConfigParser import ConfigParser

class C():
    """读取配置"""

    path = '../config/config.ini'
    def __init__(self):
        pass

    @staticmethod
    def get(sec, key):
        cp = ConfigParser()
        cp.read(self.path)
        return cp.get(sec, key)

