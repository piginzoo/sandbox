# -*- coding=utf-8 -*-
import urllib2,urllib
import json
import logging 
import traceback


def init_4_debug():
	#配置日志级别
	logging.basicConfig(level=logging.DEBUG,
					   format='%(asctime)s %(filename)s[%(lineno)d] %(levelname)s %(message)s',
					   datefmt='%H:%M:%S')

#使用
def send(apiUrl):
    
    try:
    	target_url = urllib.quote(apiUrl)
    	url = "http://suo.im/api.php?format=json&url=" + target_url
    	logging.debug("调用短URL生成[%s]",apiUrl)
        request = urllib2.Request(url)
        response = urllib2.urlopen(request)

        result_dict = json.loads(response.read())

        if response.getcode()!= 200:
        	logger.error("调用短URL服务失败：%s",result_dict["err"])
        	return None

        logging.debug("调用短URL服务返回结果:%r",result_dict["url"])

        return urllib.unquote(result_dict["url"])

    except urllib2.URLError as e:
        #traceback.print_stack()
        logging.error("调用短URL服务[%s],data[%r],发生错误[%r]", apiUrl, data,e)
        return None

if __name__ == "__main__":
    init_4_debug()
    print send("http://opcenter.xxx.corp/index.html#/monitorFlow/flowDetail?workOrderId=00EC2F262FCA49CFB8529C5BC315BD42&alarmId=86A034B317734471990381EB6C744D66&workOrderTitle=【订单超时】结算平台订单超时预警邮件&workOrderNumber=20180604123715003583&workOrderStateCode=UNTREATED&importantLevelCode=IMPORTANT&businessSystemCode=NEW_SETTLEMENT&disposeResultCode&ruleTypeCode=TRADE_OVERTIME&pstateCode=UNTREATED&bussysCode=NEW_SETTLEMENT&levelCode=IMPORTANT")