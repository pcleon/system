#!/usr/bin/env python
#coding:utf8

import logging
import time
from logging.handlers import TimedRotatingFileHandler

def initlog():
    #日志打印格式
    log_fmt = '%(asctime)s\tFile \"%(filename)s\",line %(lineno)s\t%(levelname)s: %(message)s'
    logging.basicConfig(level=logging.INFO)
    formatter = logging.Formatter(log_fmt)
    log = logging.getLogger()
    #将默认输出删除,只记录到日志
    log.handlers = []
    #创建TimedRotatingFileHandler对象
    log_file_handler = TimedRotatingFileHandler(filename="test", when="midnight", interval=1, backupCount=10)
    log_file_handler.suffix = "%Y-%m-%d_%H_%M.log"
    log_file_handler.setFormatter(formatter)
    log.addHandler(log_file_handler)
    return log


def test():
   logger.debug('debug')
   logger.info('info')
   logger.warn('warning')

logger = initlog()
while 1:
    test()
    time.sleep(2)
