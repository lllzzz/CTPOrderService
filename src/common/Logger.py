#!/usr/bin/env python
# -*- encoding:utf-8 -*-

from datetime import datetime
from C import C

class Logger():

    INFO = 'INFO'

    def __init__(self):
        self.path = C.get('path', 'log')

    def write(self, fileName, level, logName, msg = {}):
        dateTime = datetime.now()
        fileNameFormat = '%Y%m%d_' + fileName + '.log'
        fileName = datetime.strftime(dateTime, fileNameFormat)
        now = str(dateTime)
        content = now + '|[' + level + ']|' + logName;
        for k in msg:
            content += '|' + k + '|' + str(msg[k])
        content += '\n'
        filePath = self.path + '/' + fileName
        fh = open(filePath, 'a')
        fh.write(content)
        fh.close()
