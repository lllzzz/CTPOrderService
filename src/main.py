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

appKey = sys.argv[2]
trade = Trade(appKey)

srvChannel = C.get('channel', 'listen_model') % (appKey)
srv = Service([srvChannel], trade.process)

srv.run()
