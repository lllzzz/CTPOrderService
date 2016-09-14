#!/bin/bash
#
#
ps aux | grep python | grep -v grep | grep -v tradeService | grep order_service | grep main | grep "$1"
