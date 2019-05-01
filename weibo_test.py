#!/usr/bin/python
# Filename: weibo_test.py

from urllib.parse import urlencode
from pyquery import PyQuery as pq
from pymongo import MongoClient
import requests

base_url = 'https://m.weibo.cn/api/container/getIndex?'
headers = {
'Accept': 'application/json, text/plain, */*',
'MWeibo-Pwa': '1',
'Referer': 'https://m.weibo.cn/u/3713930837?jumpfrom=weibocom&sudaref=login.sina.com.cn',
'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.131 Mobile Safari/537.36',
'X-Requested-With': 'XMLHttpRequest',
'X-XSRF-TOKEN': 'e72b82'
}

def get_page(page):
    params = {
        'type':'uid',
        'value':'3713930837',
        'containerid':'1076033713930837',
        'page':page
    }
    url = base_url+ urlencode(params)
    try:
        response = requests.get(url,headers=headers)
        if response.status_code == 200:
            return response.json()
    except requests.ConnectionError as e:
        print('Error',e.args)

def parse_page(json):
    if json:
        items = json.get('data').get('cards')
        for item in items:
            item = item.get('mblog')
            weibo={}
            weibo['id'] = item.get('id')
            weibo['text'] = pq(item.get('text')).text()
            weibo['attitudes'] = item.get('attitudes_count')
            weibo['comments'] = item.get('comments_count')
            weibo['reports'] = item.get('reports_count')
            yield weibo

client = MongoClient()
db = client['weibo']
collection = db['weibo']

def save_to_mongo(result):
    if collection.insert_one(result):
        print('Saved to Mongo')

if __name__ == '__main__':
    for page in range(1,11):
        json = get_page(page)
        results = parse_page(json)
        for result in results:
            print(result)
        save = save_to_mongo(result)

