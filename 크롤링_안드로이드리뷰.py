#!/usr/bin/env python
# coding: utf-8

# In[ ]:


from selenium import webdriver # Webdriver 실행 
from bs4 import BeautifulSoup
import csv    
import requests
import re
import time
from gspread_dataframe import get_as_dataframe, set_with_dataframe
from oauth2client.service_account import ServiceAccountCredentials
import gspread
import pandas as pd
import datetime

# 사용자명 | 별점 | 날짜 | 내용 | 탈잉 대댓글


def get_date_from_gs(worksheet, spreadsheet_url):
    doc = gc.open_by_url(spreadsheet_url)
    worksheet = doc.worksheet(worksheet)
    
    return worksheet


def get_app_review(worksheet, review_div_list):
    
    data_all_list = []
    for each_review in review_div_list:

        
        user_name = each_review.select("span.X43Kjb")[0].text
        star = str(each_review.select("div.pf5lIe")[0]).split("별표 5개 만점에 ")[1][:1] 

        date = each_review.select("span.p2TkOb")[0].text
        year = int(date.split("년")[0].strip())
        month = int(date.split("월")[0].split("년")[1].strip())
        day = int(date.split("월")[1].split("일")[0].strip())
        datetime_string = datetime.date(year, month, day).strftime("%Y-%m-%d")

        content = each_review.select("div.UD7Dzf")[0].text

        content_reply = ""
        try:
            content_reply_date = each_review.select("div.LVQB0b")[0].text.split("일")[0].strip() + "일"
            content_reply = each_review.select("div.LVQB0b")[0].text.split(content_reply_date)[1].strip()
        except:
            pass

        data_list = []

        data_list.append(user_name)
        data_list.append(star)
        data_list.append(datetime_string)
        data_list.append(content)
        data_list.append(content_reply)

        data_all_list.append(data_list)
        #print(user_name, star, datetime_string, content, content_reply)

    df = pd.DataFrame(data_all_list)
    set_with_dataframe(worksheet, df, row = 2, include_column_header=False)
    
    
    
if __name__ == "__main__": 
    
    # connecting SpreadSheet
    scope = [
    'https://spreadsheets.google.com/feeds',
    'https://www.googleapis.com/auth/drive',
    ]
    json_file_name = 'C:/python/gspread/gspread-279407-99041af3d294.json'
    credentials = ServiceAccountCredentials.from_json_keyfile_name(json_file_name, scope)
    gc = gspread.authorize(credentials)    
    
    
    dr = webdriver.Chrome('C:/python/chromedriver.exe') # 창 열기 
    dr.implicitly_wait(3)
    dr.get('https://play.google.com/store/apps/details?id=com.taling&showAllReviews=true')
    
    # 화살표 누르기
    element1 = dr.find_element_by_xpath('//*[@id="fcxH9b"]/div[4]/c-wiz/div/div[2]/div/div/main/div/div[1]/div[2]/c-wiz/div[1]/div/div[1]/div[2]/span')
    element1.click()
    dr.implicitly_wait(3)

    # 최신순 클릭하기
    element2 = dr.find_element_by_xpath('//*[@id="fcxH9b"]/div[4]/c-wiz/div/div[2]/div/div/main/div/div[1]/div[2]/c-wiz/div[1]/div/div[2]/div[1]/span')
    element2.click()
    dr.implicitly_wait(3)

    # Get scroll height
    SCROLL_PAUSE_TIME = 2
    last_height = dr.execute_script("return document.body.scrollHeight")        
    while True:
        # Scroll down to bottom                                                    
        dr.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # Wait to load page
        time.sleep(SCROLL_PAUSE_TIME)                                              
        dr.execute_script("window.scrollTo(0, document.body.scrollHeight-50);") 
        time.sleep(SCROLL_PAUSE_TIME)

        # Calculate new scroll height and compare with last scroll height            
        new_height = dr.execute_script("return document.body.scrollHeight")

        # 더보기가 없어서 오류 걸리면  탈출
        try:
            if new_height == last_height:     
                # 더보기 클릭
                element3 = dr.find_element_by_xpath('//*[@id="fcxH9b"]/div[4]/c-wiz/div/div[2]/div/div/main/div/div[1]/div[2]/div[2]/div/span/span')
                element3.click()
                time.sleep(SCROLL_PAUSE_TIME)
        except:
            break

        last_height = new_height
        
        
    html = dr.page_source
    soup = BeautifulSoup(html, 'html.parser')
    
    review_div_list = soup.select("div.d15Mdf")
    app_review_ws = get_date_from_gs('android_app_review' , 'https://docs.google.com/spreadsheets/d/1tqZpknT5ztWyWWKi0U1rdTALxguJrWq7fXMEBUpbJGg/edit#gid=633734062')

    get_app_review(app_review_ws, review_div_list)

