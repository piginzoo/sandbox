#-*- coding:utf-8 -*-
import logging as logger
import logging.config,sys

reload(sys)
sys.setdefaultencoding('utf-8')

#配置日志级别
logger.config.fileConfig("log.conf")

file_logger = logger.getLogger("log")

history_logger = logger.getLogger("history")

file_logger.info("file_logger")
file_logger.info("file_logger")

history_logger.info("history_logger")
history_logger.info("history_logger")