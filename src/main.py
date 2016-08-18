#!/usr/bin/env python
# -*- encoding:utf-8 -*-

import sys
sys.path.append('../src/common')
import warnings
warnings.filterwarnings('ignore')

from Logger import Logger
from Service import Service
from C import C
from Trade import Trade

appKey = sys.argv[1]
trade = Trade(appKey)

srvChannel = C.get('channel', 'service') % (appKey)
srv = Service(appKey, [srvChannel], trade.process)

srv.run()
logger = Logger()
logger.write('trade_' + appKey, Logger.INFO, 'main[~]')
