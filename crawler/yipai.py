import json
import logging
import os
import time

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from tqdm import tqdm

logger = logging.getLogger(__name__)

url = 'https://mall.epec.com/ecmall/companyStandardRanking/subTotal.do'

header = {
    'method': 'POST',
    'scheme': 'https',
    'accept': '*/*',
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'zh-CN,zh;q=0.9',
    'cache-control': 'no-cache',
    'content-type': 'application/json',
    'origin': 'https://mall.epec.com',
    'pragma': 'no-cache',
    'referer': 'https://mall.epec.com/ecmall/companyStandardRanking/main.do?type=0&businessModel=102',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36'
}


def test_crawle():
    """
    这个是一个测试方法
    https://mall.epec.com/ecmall/companyStandardRanking/subTotal.do
    {"businessModel":"102","pageStart":"20","pageLimit":"20"}
                            ~~~~~~~~~
                            pageStart开始为0，最大25080，步长20
    可以通过这个命令直接测试：
    curl -d "{\"businessModel\":\"102\",\"pageStart\":\"20\",\"pageLimit\":\"20\"}" -X POST -H "Content-type: application/json" https://mall.epec.com/ecmall/companyStandardRanking/subTotal.do
    """

    if os.path.exists("test.html"):
        content = open("test.html", "r", encoding='utf-8').read()
        logger.debug("加载调试页面")
    else:
        data = {"businessModel": 102, "pageStart": 20, "pageLimit": 20}
        r = requests.post(url, data=json.dumps(data), headers=header)
        content = str(r.content, encoding="utf-8")
        open("test.html", "w", encoding='utf-8').write(content)
        logger.debug("保存调试页面")

    bs = BeautifulSoup(content, 'html.parser')
    companies = bs.select("#eva_cenbox tr")
    for c in companies:
        tds = c.find_all('td')
        if len(tds)!=3:
            logger.warning("TD长度不为3，忽略")
            continue
        id = tds[0].text
        company = tds[1].text
        index = tds[2].text
        logger.debug("%s,%s,%s",id,company,index)



def crawle(start, file):
    """
    https://mall.epec.com/ecmall/companyStandardRanking/subTotal.do
    {"businessModel":"102","pageStart":"20","pageLimit":"20"}
                            ~~~~~~~~~
                            pageStart开始为0，最大25080，步长20
    可以通过这个命令直接测试：
    curl -d "{\"businessModel\":\"102\",\"pageStart\":\"20\",\"pageLimit\":\"20\"}" -X POST -H "Content-type: application/json" https://mall.epec.com/ecmall/companyStandardRanking/subTotal.do
    """

    data = {"businessModel": 102, "pageStart": start, "pageLimit": 20}
    r = requests.post(url, data=json.dumps(data), headers=header)
    content = str(r.content, encoding="utf-8")

    bs = BeautifulSoup(content, 'html.parser')
    companies = bs.select("#eva_cenbox tr")
    for c in companies:

        tds = c.find_all('td')
        if len(tds)!=3:
            # logger.warning("TD长度[%d]不为3，忽略",len(tds))
            continue
        id = tds[0].text
        company = tds[1].text
        index = tds[2].text

        file.write(id+","+company+","+index)
        file.write("\n")
        file.flush()


def main(max_start):
    file = open("company.txt", "w", encoding='utf-8')

    pbar = tqdm(total=max_start)
    for start in range(0, max_start + 20, 20):

        try:
            crawle(start, file)
        except Exception as e:
            logger.exception("爬取第%d条出现问题，继续", start)
        finally:
            time.sleep(1)
            pbar.update(20)

    pbar.close()
    file.close()


# python yipai.py
if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG, format="[%(levelname)s] %(message)s")
    main(max_start=25080)

    # 尝试爬
    #main(max_start=60)

    # 调试程序
    # test_crawle()
