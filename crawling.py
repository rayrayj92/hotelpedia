import requests
from bs4 import BeautifulSoup

from pymongo import MongoClient


client = MongoClient('mongodb://test:test@localhost')
db = client.dbHotelpedia

headers = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
data = requests.get('https://www.goodchoice.kr/product/search/2/2052?sel_date=2021-03-05&sel_date2=2021-03-06',headers=headers)

soup = BeautifulSoup(data.text, 'html.parser')

# 호텔 정보
# 이름 : #poduct_list_area > li:nth-child(2) > a > div > div.name > strong
# 평점 : #poduct_list_area > li:nth-child(2) > a > div > div.name > p.score > em
# 가격 : #poduct_list_area > li:nth-child(23) > a > div > div.price > p > b
# 위치 : #poduct_list_area > li:nth-child(23) > a > div > div.name > p:nth-child(4)
# 이미지 url : #poduct_list_area > li:nth-child(23) > a > p > img

lis = soup.select('#poduct_list_area > li')
for li in lis:
    hotel_rate_em = li.select_one('a > div > div.name > p.score > em')
    if hotel_rate_em is not None:
        hotel_name = li.select_one('a > div > div.name > strong').text
        hotel_rate = hotel_rate_em.text
        hotel_price = li.select_one('a > div > div.price > p > b').text
        hotel_location = li.select_one('a > div > div.name > p:nth-child(4)').text.strip()
        hotel_imageUrl = li.select_one('a > p > img')['data-original']
        print(hotel_name, hotel_rate, hotel_location, hotel_price, hotel_imageUrl)
        doc = {
            'name': hotel_name,
            'rate': hotel_rate,
            'location': hotel_location,
            'price': hotel_price,
            'imageUrl': hotel_imageUrl,
            'state': '제주',
            'city': '서귀포시'
        }
        db.hotels.insert_one(doc)
        print('완료', hotel_name)


