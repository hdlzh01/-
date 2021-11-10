import requests
import re
import os
import sys
import json
from pyquery import PyQuery as pq
import time
import random
#from fake_useragent import UserAgent




s = requests.Session()
headers = {
            "User-Agent":"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
    }
login_url = 'https://accounts.douban.com/passport/login?source=movie'

def login_duban():
    login_data = {
        'name': 'dream92',
        'password': 'Qwerty4321',
        'remember': 'false'
    }
    try:
        r = s.post(login_url, headers=headers, data=login_data)
    except:
        print('登录请求失败')
        return 0
    return 1


def get_movie():
    movie_list = []
    n = 1000
    for k in range(0, n, 50):
        #headers = {"User-Agent": UserAgent(verify_ssl=False).random}
        url = 'https://movie.douban.com/j/search_subjects?type=movie&tag=%E7%83%AD%E9%97%A8&page_limit=50&page_start=' + str(k)
        r = s.get(url, headers=headers)
        text = r.text
        print(text)
        json_text = json.loads(text)['subjects']

        for i in range(len(json_text)):
            movie_list.append(json_text[i]['url'])
            print(json_text[i]['url'])
        time.sleep(1)

    return movie_list





if login_duban():
    print("登录成功")
    movie = get_movie()
    time.sleep(10)

    n1 = 1000
    for m in movie:
        for pos in range(0, n1, 20):
            comment_url = m + 'comments?start=' + str(pos) + '&limit=20&status=P&sort=new_score'

            r = s.get(comment_url, headers=headers)
            text = r.text
            con = re.findall('<span class=\"short\">.*?</span>', text)

            for i in range(len(con)):
                con[i] = con[i][20:-7]
            time.sleep(1)


