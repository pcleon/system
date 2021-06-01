#coding: utf-8
import logging
import os
from logging.handlers import TimedRotatingFileHandler

def mylog(logname, interval=1, backup=30):
    logdir = os.path.dirname(logname)
    if not os.path.exists(logdir) and logdir != '':
        os.mkdir(logdir)

    logger = logging.getLogger()
    formatter = logging.Formatter('%(asctime)s|%(module)s|%(lineno)s|%(levelname)s|%(message)s')
    #日志回滚与定期删除
    rotating_handler = TimedRotatingFileHandler(
        logname, when='midnight', interval=interval, backupCount=backup
    )
    rotating_handler.setFormatter(formatter)
    rotating_handler.suffix = '%Y-%m-%d'
    rotating_handler.setLevel(logging.DEBUG)
    rotating_handler.setFormatter(formatter)
    if not logger.handlers:
        logger.addHandler(rotating_handler)
    logger.propagate = False
    return logger

if __name__ == '__main__':
    l = mylog('test.log')
    l.error('err')
