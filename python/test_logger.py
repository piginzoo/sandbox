#-*- coding:utf-8 -*-
import logging as logger
import logging.config,sys
from logging import handlers

# reload(sys)
# sys.setdefaultencoding('utf-8')

#配置日志级别
logger.config.fileConfig("log.conf")

file_logger = logger.getLogger("log")

history_logger = logger.getLogger("history")

file_logger.info("file_logger")
file_logger.info("file_logger")

history_logger.info("history_logger")
history_logger.info("history_logger")

logger = logging.getLogger()

_format="%(levelname)s: %(asctime)s: %(filename)s:%(lineno)d行 %(message)s"
formatter = logging.Formatter(_format)
t_handler = handlers.TimedRotatingFileHandler("test.log", when='D', backupCount=1)
t_handler.setLevel(logging.DEBUG)
t_handler.setFormatter(formatter)
logger.addHandler(t_handler)

for l in logger.handlers:
	print(l)

# # 解决console.log上出现垃圾日志的问题：https://github.com/tensorflow/tensorflow/issues/26691
import absl.logging
logging.root.removeHandler(absl.logging._absl_handler)
absl.logging._warn_preinit_stderr = False

print("xxxxxx")