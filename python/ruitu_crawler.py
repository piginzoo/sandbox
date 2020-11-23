from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium import webdriver
import urllib.request
import time


class RuituCrawler(object):
    def __init__(self):
        urls = ["http://www.ruituschool.com/150/?from=groupmessage#/list?id="] * 30
        ids = [str(i) for i in list(range(1, 31))]
        self.url_ids = [i + j for i, j in zip(urls, ids)]

        self.article_index = 0

        # 这个不用了，用上面那个
        self.root_url = "http://www.ruituschool.com/150/?from=groupmessage#/"


    def download_file(self, url, file_name):
        with urllib.request.urlopen(url) as response, open(file_name, 'wb') as out_file:
            data = response.read()  # a `bytes` object
            out_file.write(data)

    def run(self):
        cops = webdriver.ChromeOptions()
        browser = webdriver.Chrome(
            chrome_options=cops
        )

        self.article_file = open("ruitu/scripts.txt", "w", encoding="utf-8")

        for url in self.url_ids:
            self.process_one(url, browser)

        self.article_file.close()
        print("全部爬取完，合计文章数：%d", self.article_index)

    def dump_article(self, content):
        self.article_file.write("第%d篇\n" % self.article_index)
        self.article_file.write(content)
        self.article_file.write("\n\n")

    def process_one(self, url, browser):
        try:
            browser.get(url)
            WebDriverWait(browser, 20).until(
                expected_conditions.visibility_of_element_located((By.CSS_SELECTOR, '#app'))
            )
            links = browser.find_elements(By.CSS_SELECTOR, '.blockb')

            current_index = 0
            while (current_index < len(links)):
                link = links[current_index]
                link.click()
                WebDriverWait(browser, 20).until(
                    expected_conditions.visibility_of_element_located((By.CSS_SELECTOR, '#page-content'))
                )

                contents = browser.find_elements(By.CSS_SELECTOR, 'span[dir=LTR]')
                str_contents = ""
                print("开始爬取第%d篇" % self.article_index)
                for c in contents:
                    print(c.text)
                    str_contents += c.text + "\n"
                print("----------------------------------------")
                self.article_index += 1
                self.dump_article(str_contents)

                mp3s = browser.find_elements(By.CSS_SELECTOR, 'mpvoice')
                if type(mp3s) == list:
                    mp3s = mp3s[0]
                mp3_id = mp3s.get_attribute("voice_encode_fileid")
                mp3_url = "https://res.wx.qq.com/voice/getvoice?mediaid={}".format(mp3_id)
                mp3_file_name = "ruitu/"+str(self.article_index)+".mp3"
                print("下载MP3：",mp3_url, "=>", mp3_file_name)
                self.download_file(mp3_url,mp3_file_name)

                browser.back()
                time.sleep(0.5)
                browser.refresh()
                time.sleep(1)
                browser.get(url)
                WebDriverWait(browser, 20).until(
                    expected_conditions.visibility_of_element_located((By.CSS_SELECTOR, '#app'))
                )
                links = browser.find_elements(By.CSS_SELECTOR, '.blockb')
                current_index += 1

        except Exception as e:
            print("发生异常！！！")
            print(e)
        print("爬完了这个索引页：" + url)
        print("===============================================================")


if __name__ == '__main__':
    ocrCheck = RuituCrawler()
    ocrCheck.run()
