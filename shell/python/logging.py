#!/usr/bin/env python
#coding:utf8

import logging
from logging.handlers import TimedRotatingFileHandler
import time

def initLog():
    #logger
    logger = logging.getLogger('test')
    logger.setLevel(logging.WARNING)
    #file handler
    fname = 'log'
    fh = TimedRotatingFileHandler(filename = fname , when='M', interval= 1 , backupCount= 0)
    fh.suffix = "%Y%m%d_%H%M"
    #fmt
    datefmt = "%Y%m%d %H:%M:%S"
    fmt = "%(asctime)-15s %(levelname)s %(filename)s %(lineno)d %(process)d %(message)s"
    formatter = logging.Formatter(fmt, datefmt)
    #add fmt to handler
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    return logger

while 1 :
    t = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
    info = 'info ---- ' + t
    warn = 'info ---- ' + t
    err = 'info ---- ' + t
    log = initLog()
    log.info(info)
    log.warning(warn)
    log.error(err)
    time.sleep(1)
