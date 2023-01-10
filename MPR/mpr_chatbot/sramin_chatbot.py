from flask import Flask, request, jsonify,redirect
import pymysql
import urllib.request
import re
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time
import pandas as pd
application = Flask(__name__)

# STEP 2: MySQL Connection 연결
con = pymysql.connect(host="localhost",user="root",password="enffl7071!",port=3306,db="testdb",charset='utf8')

# STEP 3: Connection 으로부터 Cursor 생성
cur = con.cursor(pymysql.cursors.DictCursor)

# data = pd.read_csv("data/sramin.csv")
# local/animal 에 해당하는 값 추출 / DB에 붙어서 값 출력 OK
@application.route("/main", methods=['POST'])
def animal():
    req = request.get_json()
    search_text = req['userRequest']['utterance']
    sql = "select * from saramin where work_pos LIKE '%"+search_text+"%'"
    cur.execute(sql)
    rows = cur.fetchall()
    # print(rows)
    # search_text=re.sub(r"\s", "", search_text)
    # search_text_lst = search_text.split(',')
    # df = data[data['직무'].str.contains(search_text)].reset_index(drop=True)
    # print(req)
    # res = {
    #     "version": "2.0",
    #     "template": {
    #         "outputs": [
    #             {
    #                 "simpleText": {
    #                     "text": '테스트중.'
    #                 }
    #             }
    #         ]
    #     }
    # }
    if len(rows)>0:
        try:
            res = {
                "version": "2.0",
                "template": {
                    "outputs": [
                        {
                            "simpleText": {
                                "text": '울산에 있는 {} 관련 기업은 총 {}개 입니다.'.format(search_text,len(rows))
                            }
                        },
                        {
                            "listCard": {
                                "header": {
                                    "title": "{}에 관한 리스트 입니다.".format(search_text)
                                },
                                "items": [
                                    {
                                        "title": rows[i]['title'],
                                        "description": rows[i]['office_nm'],
                                        "link": {
                                            "web": rows[i]['url']
                                        }
                                    } for i in range(5)
                                ],
                                "buttons": [
                                    {
                                        "label": "더보기",
                                        "action": "webLink",
                                        "webLinkUrl": "https://www.saramin.co.kr/zf_user/search?search_area=main&search_done=y&search_optional_item=n&searchType=default_popular&loc_mcd=107000"
                                    }
                                ]
                            }
                        }
                    ]
                }
            }
        except:
            res = {
                "version": "2.0",
                "template": {
                    "outputs": [
                        {
                            "simpleText": {
                                "text": '울산에 있는 {} 관련 기업은 총 {}개 입니다.'.format(search_text, len(rows))
                            }
                        },
                        {
                            "listCard": {
                                "header": {
                                    "title": "{}에 관한 리스트 입니다.".format(search_text)
                                },
                                "items": [
                                    {
                                        "title": rows[i]['title'],
                                        "description": rows[i]['office_nm'],
                                        "link": {
                                            "web": rows[i]['url']
                                        }
                                    } for i in range(len(rows))
                                ],
                                "buttons": [
                                    {
                                        "label": "더보기",
                                        "action": "webLink",
                                        "webLinkUrl": "https://www.saramin.co.kr/zf_user/search?search_area=main&search_done=y&search_optional_item=n&searchType=default_popular&loc_mcd=107000"
                                    }
                                ]
                            }
                        }
                    ]
                }
            }
    else:
        res = {
            "version": "2.0",
            "template": {
                "outputs": [
                    {
                        "simpleText": {
                            "text": '데이터가 존재하지 않습니다 다시 입력해주세요.'
                        }
                    }
                ]
            }
        }
    # con.close()
    # 답변 전송
    return jsonify(res)

if __name__ == "__main__":
    application.run(host='0.0.0.0', port=9999, threaded=True)