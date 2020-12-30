import logging,time
import os
from logging.handlers import TimedRotatingFileHandler

class Logger(object):
    def __init__(self, logname, day=30):
        logdir = os.path.dirname(logname)
        if not os.path.exists(logdir) and logdir != '':
            os.mkdir(logdir)
        self.logname = logname
        self.day = day
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.NOTSET)

        formatter = logging.Formatter('%(asctime)s|%(module)s|%(lineno)s|%(levelname)s|%(message)s')
        # 创建一个FileHandler，用于写到本地
        fh = TimedRotatingFileHandler(filename=self.logname, when="midnight", interval=1, backupCount=self.day)
        fh.suffix = '%Y-%m-%d'
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(formatter)
        if not self.logger.handlers:
            self.logger.addHandler(fh)

    def debug(self, message):
        self.logger.debug(message)

    def info(self, message):
        self.logger.info(message)

    def warn(self, message):
        self.logger.warning(message)

    def error(self, message):
        self.logger.error(message)

    def critical(self, message):
        self.logger.critical(message)


if __name__ == '__main__':
    l = Logger('test.log')
    l.info('aa')
    x = Logger('test.log')
    x.error('aa')
