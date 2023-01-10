from flask import Flask, request, jsonify,redirect
import pymysql
import urllib.request
import re
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time

application = Flask(__name__)

# STEP 2: MySQL Connection 연결
con = pymysql.connect(host="localhost",user="root",password="enffl7071!",port=3306,db="testdb",charset='utf8')

# STEP 3: Connection 으로부터 Cursor 생성
cur = con.cursor()

# local/animal 에 해당하는 값 추출 / DB에 붙어서 값 출력 OK
@application.route("/main", methods=['POST'])
def animal():
    req = request.get_json()
    search_text = req['userRequest']['utterance']
    search_text=re.sub(r"\s", "", search_text)
    search_text_lst = search_text.split(',')
    db_lst = []
    cr_lst = []
    # print(search_text_lst)
    for i in range(len(search_text_lst)):
        if search_text_lst[i].strip()[-1] == '@':
            cr_lst.append(search_text_lst[i].strip()[:-1].strip())
        elif search_text_lst[i][-1] == '$':
            db_lst.append(search_text_lst[i].strip()[:-1].strip())
        else:
            res = {
                "version": "2.0",
                "template": {
                    "outputs": [
                        {
                            "simpleText": {
                                "text": '알 수 없는 명령어 입니다. 형식을 다시 확인 후 입력해주세요.'
                            }
                        }
                    ]
                }
            }
    if len(db_lst)!=0:
        #  # DB에 연결 하여 DB에 있는 값 출력
        dict = {}
        for i in range(len(db_lst)):
            try:
                # # STEP 4: SQL문 실행 및 Fetch
                sql = """SELECT name FROM member where name=%s;"""
                param = db_lst[i].strip()
                cur.execute(sql, param)

                # 데이타 Fetch
                rows = cur.fetchall()
                dict[param]=len(rows)
            except Exception as e:
                print(e)
                # res = {
                #     "version": "2.0",
                #     "template": {
                #         "outputs": [
                #             {
                #                 "simpleText": {
                #                     "text": '알 수 없는 명령어 입니다.'
                #                 }
                #             }
                #         ]
                #     }
                # }
            else:
                res = {
                    "version": "2.0",
                    "template": {
                        "outputs": [
                            {
                                "simpleText": {
                                    "text": '입력하신 {}에 대한 데이터가 존재하지 않습니다. 다시 입력해주세요'.format(key)
                                }
                            } if value==0 else {
                                "simpleText": {
                                    "text": '입력하신 {}에 대한 값: {}'.format(key,value)
                                    # "text" : "테스트중입니다."
                                }
                            }for key,value in dict.items()
                        ]
                    }
                }
    elif search_text.strip()[-1] == '@':
        key_wd = search_text.strip()[:-1]
        key_wd_lst=key_wd.split('/')
        tmp_text = key_wd_lst[0].encode("utf-8")
        tmp_text = str(tmp_text)[2:-1].replace('\\x', '%')
        options = webdriver.ChromeOptions()
        options.add_argument("headless")

        # 2. 웹페이지 열기 및 입력
        # chrome_path = "chromedriver.exe"
        # driver = webdriver.Chrome(chrome_path, options=options)
        # driver.maximize_window()
        # url = "https://www.naver.com/"
        # driver.get(url)
        #
        # element = driver.find_element("id", "query")
        # driver.find_element("id", "query").click()
        # element.send_keys(key_wd_lst[0])
        # element.send_keys('\n')
        try:
            if key_wd_lst[1] == '뉴스':
                chrome_path = "chromedriver.exe"
                driver = webdriver.Chrome(chrome_path, options=options)
                url = "https://search.naver.com/search.naver?where=news&query={}&sm=tab_opt&sort=0&photo=0&field=0&pd=3&ds={}&de={}&docid=&related=0&mynews=0&office_type=0&office_section_code=0&news_office_checked=&nso=so%3Ar%2Cp%3Afrom20221201to20221231&is_sug_officeid=0" \
                    .format(tmp_text, key_wd_lst[2], key_wd_lst[3])
                driver.get(url)

                url_all_list = []  # 조회할 블로그의 URL 정보 저장용 리스트
                img_all_list = []
                title_all_list = []
                total_lst = []
                no = 1
                collect = int(key_wd_lst[4])
                html = driver.page_source
                soup = BeautifulSoup(html, 'html.parser')
                url_list_1 = soup.find('ul', 'list_news').find_all('li', 'bx')
                for i in range(0, len(url_list_1)):
                    try:
                        url_all_list.append(url_list_1[i].find("a", "news_tit")["href"])
                        title_all_list.append(url_list_1[i].find("a", "news_tit")["title"])
                        img_all_list.append(url_list_1[i].find("img", "thumb api_get")['src'])

                    except:
                        img_all_list.append(
                            'https://search.pstatic.net/common/?src=http%3A%2F%2Fblogfiles.naver.net%2FMjAyMjExMDlfMTI1%2FMDAxNjY3OTg0NjMxMTA4.y0DEJXZK5oaxrYuynVp-T9m6kj6g2GvRd7r3EcvM-WYg.8yMJMP1OhGsOpiFexVbkIkv_cheBQRSDx1FOrOtf-WYg.JPEG.v1agra%2FIMG_3589.JPG&type=sc960_832')
                    no += 1
                    if no > collect:
                        break

                res = {
                    "version": "2.0",
                    "template": {
                        "outputs": [
                            {
                                "listCard": {
                                    "header": {
                                        "title": "{}에 관한 {}입니다.".format(key_wd_lst[0],key_wd_lst[1])
                                    },
                                    "items": [
                                        {
                                            "title": title_all_list[i],
                                            # "description": "새로운 AI의 내일과 일상의 변화",
                                            "imageUrl": img_all_list[i],
                                            "link": {
                                                "web": url_all_list[i]
                                            }
                                        } for i in range(collect)
                                    ],
                                    "buttons": [
                                        {
                                            "label": "더보기",
                                            "action": "webLink",
                                            "webLinkUrl": url
                                        }
                                    ]
                                }
                            }
                        ]
                    }
                }
            elif key_wd_lst[1] == '블로그':
                str_date = key_wd_lst[2].replace('.', '')
                end_date = key_wd_lst[3].replace('.', '')
                chrome_path = "chromedriver.exe"
                driver = webdriver.Chrome(chrome_path, options=options)
                url = "https://search.naver.com/search.naver?where=blog&query={}&sm=tab_opt&nso=so:r,p:from{}to{}" \
                    .format(tmp_text, str_date, end_date)
                driver.get(url)
                # 조회 시작 날짜와 종료 날짜 선택하기
                url_all_list = []  # 조회할 블로그의 URL 정보 저장용 리스트
                img_all_list = []
                title_all_list = []
                no = 1
                collect = int(key_wd_lst[4])
                html = driver.page_source
                soup = BeautifulSoup(html, 'html.parser')
                url_list_1 = soup.find('ul', 'lst_total').find_all('li', 'bx')

                for i in range(0, len(url_list_1)):
                    try:
                        title_all_list.append(url_list_1[i].find("a", "api_txt_lines total_tit").get_text())
                        url_all_list.append(url_list_1[i].find("a", "api_txt_lines total_tit")["href"])
                        img_all_list.append(url_list_1[i].find("img", "thumb api_get")['src'])

                    except:
                        img_all_list.append(
                            'https://search.pstatic.net/common/?src=http%3A%2F%2Fblogfiles.naver.net%2FMjAyMjEyMjlfMjA1%2FMDAxNjcyMjc5MjQwNTUz.5asLmhWjfRFmxLs-tIDg8UVj6A_n-XUY-NjEa3_-XnQg.xiqJA7fFM--hah4eF9j2HVLqWyaasEo1tcF6SHWyCIUg.PNG.anothergyeol%2Fimage.png&type=sc960_832')
                    no += 1
                    if no > collect:
                        break
                res = {
                    "version": "2.0",
                    "template": {
                        "outputs": [
                            {
                                "listCard": {
                                    "header": {
                                        "title": "{}에 관한 {}입니다.".format(key_wd_lst[0], key_wd_lst[1])
                                    },
                                    "items": [
                                        {
                                            "title": title_all_list[i],
                                            "imageUrl": img_all_list[i],
                                            "link": {
                                                "web": url_all_list[i]
                                            }
                                        } for i in range(collect)
                                    ],
                                    "buttons": [
                                        {
                                            "label": "더보기",
                                            "action": "webLink",
                                            "webLinkUrl": url
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
                                "text": '형식 확인 후 다시 입력해주세요!\n예시1)"검색어"/"뉴스 or 블로그"/시작날짜/종료날짜/ 출력하고자 하는 갯수(3~5개) @"\n->지정날짜에서 갯수만큼 출력\n예시2)"검색어/뉴스 or 블로그 @" \n-> 최신순으로 3개 출력.'
                            }
                        }
                    ]
                }
            }
        if len(key_wd_lst)==2:
            if key_wd_lst[1] == '뉴스':
                chrome_path = "chromedriver.exe"
                driver = webdriver.Chrome(chrome_path, options=options)
                url = "https://search.naver.com/search.naver?where=news&query={}&sm=tab_opt&sort=1&photo=0&field=0&pd=0&ds=&de=&docid=&related=0&mynews=0&office_type=0&office_section_code=0&news_office_checked=&nso=so%3Add%2Cp%3Aall&is_sug_officeid=0" \
                    .format(tmp_text)
                driver.get(url)

                url_all_list = []  # 조회할 블로그의 URL 정보 저장용 리스트
                img_all_list = []
                title_all_list = []
                total_lst = []
                no = 1
                collect = 3
                html = driver.page_source
                soup = BeautifulSoup(html, 'html.parser')
                url_list_1 = soup.find('ul', 'list_news').find_all('li', 'bx')
                for i in range(0, len(url_list_1)):
                    try:
                        url_all_list.append(url_list_1[i].find("a", "news_tit")["href"])
                        title_all_list.append(url_list_1[i].find("a", "news_tit")["title"])
                        img_all_list.append(url_list_1[i].find("img", "thumb api_get")['src'])

                    except:
                        img_all_list.append(
                            'https://search.pstatic.net/common/?src=http%3A%2F%2Fblogfiles.naver.net%2FMjAyMjExMDlfMTI1%2FMDAxNjY3OTg0NjMxMTA4.y0DEJXZK5oaxrYuynVp-T9m6kj6g2GvRd7r3EcvM-WYg.8yMJMP1OhGsOpiFexVbkIkv_cheBQRSDx1FOrOtf-WYg.JPEG.v1agra%2FIMG_3589.JPG&type=sc960_832')
                    no += 1
                    if no > collect:
                        break

                res = {
                    "version": "2.0",
                    "template": {
                        "outputs": [
                            {
                                "listCard": {
                                    "header": {
                                        "title": "{}에 관한 {}입니다.".format(key_wd_lst[0], key_wd_lst[1])
                                    },
                                    "items": [
                                        {
                                            "title": title_all_list[i],
                                            # "description": "새로운 AI의 내일과 일상의 변화",
                                            "imageUrl": img_all_list[i],
                                            "link": {
                                                "web": url_all_list[i]
                                            }
                                        } for i in range(collect)
                                    ],
                                    "buttons": [
                                        {
                                            "label": "더보기",
                                            "action": "webLink",
                                            "webLinkUrl": url
                                        }
                                    ]
                                }
                            }
                        ]
                    }
                }
            elif key_wd_lst[1] == '블로그':
                chrome_path = "chromedriver.exe"
                driver = webdriver.Chrome(chrome_path, options=options)
                url = "https://search.naver.com/search.naver?where=blog&query={}&sm=tab_opt&nso=so%3Add%2Cp%3Aall" \
                    .format(tmp_text)
                driver.get(url)
                # 조회 시작 날짜와 종료 날짜 선택하기
                url_all_list = []  # 조회할 블로그의 URL 정보 저장용 리스트
                img_all_list = []
                title_all_list = []
                no = 1
                collect = 3
                html = driver.page_source
                soup = BeautifulSoup(html, 'html.parser')
                url_list_1 = soup.find('ul', 'lst_total').find_all('li', 'bx')

                for i in range(0, len(url_list_1)):
                    try:
                        title_all_list.append(url_list_1[i].find("a", "api_txt_lines total_tit").get_text())
                        url_all_list.append(url_list_1[i].find("a", "api_txt_lines total_tit")["href"])
                        img_all_list.append(url_list_1[i].find("img", "thumb api_get")['src'])

                    except:
                        img_all_list.append(
                            'https://search.pstatic.net/common/?src=http%3A%2F%2Fblogfiles.naver.net%2FMjAyMjEyMjlfMjA1%2FMDAxNjcyMjc5MjQwNTUz.5asLmhWjfRFmxLs-tIDg8UVj6A_n-XUY-NjEa3_-XnQg.xiqJA7fFM--hah4eF9j2HVLqWyaasEo1tcF6SHWyCIUg.PNG.anothergyeol%2Fimage.png&type=sc960_832')
                    no += 1
                    if no > collect:
                        break
                res = {
                    "version": "2.0",
                    "template": {
                        "outputs": [
                            {
                                "listCard": {
                                    "header": {
                                        "title": "{}에 관한 {}입니다.".format(key_wd_lst[0], key_wd_lst[1])
                                    },
                                    "items": [
                                        {
                                            "title": title_all_list[i],
                                            # "description": "새로운 AI의 내일과 일상의 변화",
                                            "imageUrl": img_all_list[i],
                                            "link": {
                                                "web": url_all_list[i]
                                            }
                                        } for i in range(collect)
                                    ],
                                    "buttons": [
                                        {
                                            "label": "더보기",
                                            "action": "webLink",
                                            "webLinkUrl": url
                                        }
                                    ]
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