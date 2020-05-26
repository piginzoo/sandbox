from a import a
from p.b import b
import logging
from logging import handlers
import os,time
import os.path as ops
import datetime

def init_logger(level=logging.DEBUG,
                when="D",
                backup=7,
                _format="%(levelname)s: %(asctime)s: %(filename)s:%(lineno)d行 %(message)s"):
    log_path = ops.join(os.getcwd(), '../log/test.log')
    _dir = os.path.dirname(log_path)
    if not os.path.isdir(_dir):
        os.makedirs(_dir)

    logger = logging.getLogger()
    if not logger.handlers:
        formatter = logging.Formatter(_format)
        logger.setLevel(level)

        handler = handlers.TimedRotatingFileHandler(log_path, when=when, backupCount=backup)
        handler.setLevel(level)
        handler.setFormatter(formatter)
        logger.addHandler(handler)

        handler = logging.StreamHandler()
        handler.setLevel(level)
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    return logger


if __name__ == '__main__':
	init_logger()

	my_logger = logging.getLogger(__name__)
	while True:
		time.sleep(1)
		a()
		b()