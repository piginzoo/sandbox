import requests
from bs4 import BeautifulSoup

url = "https://tao.360che.com/list/"
print("准备爬取卡车之家二手车："+ url)

response = requests.get(url)
soup = BeautifulSoup(response.content, 'lxml')

url_chapters =     soup.select('body > div.container > div > div > div.truck-list-list > div.clearfix > a > div.content')
title_chapters =   soup.select('body > div.container > div > div > div.truck-list-list > div.clearfix > a > div.content > div.title')
details_chapters = soup.select('body > div.container > div > div > div.truck-list-list > div.clearfix > a > div.content > div.info')
price_chapters =   soup.select('body > div.container > div > div > div.truck-list-list > div.clearfix > a > div.content > div.price')

#for url,title, details,price in zip(url_chapters,title_chapters,details_chapters,price_chapters):
cars = []
for content in  url_chapters :
    #print(type(content))                             
    divs = content.find_all("div")
    car = {}
    for div in divs:
        # print(div['class'][0])
        if div['class'][0]=="info":
            print("info:",div.get_text())
            car['info'] = div.get_text()
        if div['class'][0]=="title":
            print("title:",div.get_text())
            car['title'] = div.get_text()
        if div['class'][0]=="price":
            print("price:",div.get_text())
            car['price'] = div.get_text()
        if div['class'][0]=="label":
            print("label:",div.get_text())
            car['label'] = div.get_text()
    cars.append(car)
    print("=========================")


print(cars)
