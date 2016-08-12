#!/usr/bin/env python
# -*- encoding:utf-8 -*-

import sys
sys.path.append('../src/common')
import os

from Rds import Rds
from C import C

if len(sys.argv) == 1:
    print '''启动/停止系统：./tradeService start/stop
查看状态：./tradeService status'''
    sys.exit()

cmd = sys.argv[1]
appKey = C.get('sys', 'appKey')

if cmd == 'start':
    os.system('python ../src/main.py ' + appKey + ' &')
elif cmd == 'stop':
    rds = Rds.getSender()
    ch = C.get('channel', 'service') + appKey
    rds.publish(ch, 'stop')
elif cmd == 'status':
    os.system('./find.sh ' + appKey)