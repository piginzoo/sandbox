# -*- coding:utf-8 -*-
import logging.config,sys
import logging

reload(sys)
sys.setdefaultencoding('utf-8')

history_logger_names = []

def init():
	#配置日志级别
	logging.config.fileConfig("log.conf")

def info(msg, *args):
	logger = logging.getLogger("log")
	logger.info(msg,args)

def debug(msg, *args):
	logger = logging.getLogger("log")
	logger.debug(msg,args)

#记录
def history(type,group,user,message):
	if type !="qq" and type!= "wechat":
		raise ValueError("the type must be qq or wechat")

	if group is None or group == "":
		raise ValueError("the group name must not be null")

	history_file_name = type+"."+group+".his"

	history_logger = _get_logger(history_file_name)

	history_logger.info("{}>{}:{}".format(group,user,message))

def _get_logger(logger_name):
	logger = logging.getLogger(logger_name)
	if logger_name in history_logger_names: return logger

	formatter = logging.Formatter('%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
	fileHandler = logging.FileHandler("log/"+logger_name, mode='a')
	fileHandler.setFormatter(formatter)

	logger.setLevel(logging.INFO)
	logger.addHandler(fileHandler)

	history_logger_names.append(logger_name)

	return logger

if __name__ == '__main__':
	init()

	history("qq","group","user","xxxxxxxxx")

	info("log %s","ssss")
	info("log %r",["yyyy"])

	debug("log %r",["debug"])