import requests
from bs4 import BeautifulSoup

def books():
    books = {}
    books['61499'] = '通幽大圣'
    # books['24277'] = '飞剑问道'
    # books['3773'] = '三寸人间'
    # books['12056'] = '修罗刀帝'
    # books['9751'] = '灵武帝尊'

    for k, v in books.items():
        #每一个小说
        print(k, v)
        url = "https://www.biqiuge.com/book/" + k
        print("准备爬取书：",v)
        response = requests.get(url)

        soup = BeautifulSoup(response.content, 'lxml')

        # 第三步：解析网页数据
        book_chapters = soup.select('.listmain dd a')
        for b in book_chapters:
            # print(b)
            print("URL："+"https://www.biqiuge.com"+b['href'])
            print("标题："+b.text)

            '''
            TODO:
                然后这里，你需要再调用你的那个section函数，爬取每一章，
                这是一个二重循环了，即先爬目录，然后再爬目录里面的每一章
            '''

if __name__ == '__main__':
    books()