#!/usr/bin/env python
# -*- encoding:utf-8 -*-

import sys
sys.path.append('../src/common')
import os

from Rds import Rds
from C import C

if len(sys.argv) == 1:
    print '''启动/停止系统：./tradeService start/stop appKey
查看状态：./tradeService status'''
    sys.exit()

cmd = sys.argv[1]
if cmd != 'status':
    appKey = sys.argv[2]

if cmd == 'start':
    os.system('python ../src/main.py trade_service ' + appKey + ' &')
elif cmd == 'stop':
    rds = Rds.getSender()
    ch = C.get('channel', 'listen_model') % (appKey)
    rds.publish(ch, 'stop')
elif cmd == 'status':
    os.system('./find.sh')
