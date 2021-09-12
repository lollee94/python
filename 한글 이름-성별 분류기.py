#!/usr/bin/env python
# coding: utf-8

# In[1]:


from sklearn.preprocessing import LabelEncoder
import pandas as pd
import re
import sys
from catboost import CatBoostClassifier

pd.options.display.max_columns = 100
pd.options.display.max_rows = 100
# 유니코드 한글 시작 : 44032, 끝 : 55199

BASE_CODE, CHOSUNG, JUNGSUNG = 44032, 588, 28

# 초성 리스트. 00 ~ 18
CHOSUNG_LIST = ['ㄱ', 'ㄲ', 'ㄴ', 'ㄷ', 'ㄸ', 'ㄹ', 'ㅁ', 'ㅂ', 'ㅃ', 'ㅅ', 'ㅆ', 'ㅇ', 'ㅈ', 'ㅉ', 'ㅊ', 'ㅋ', 'ㅌ', 'ㅍ', 'ㅎ']

# 중성 리스트. 00 ~ 20
JUNGSUNG_LIST = ['ㅏ', 'ㅐ', 'ㅑ', 'ㅒ', 'ㅓ', 'ㅔ', 'ㅕ', 'ㅖ', 'ㅗ', 'ㅘ', 'ㅙ', 'ㅚ', 'ㅛ', 'ㅜ', 'ㅝ', 'ㅞ', 'ㅟ', 'ㅠ', 'ㅡ', 'ㅢ', 'ㅣ']

# 종성 리스트. 00 ~ 27 + 1(1개 없음)
JONGSUNG_LIST = [' ', 'ㄱ', 'ㄲ', 'ㄳ', 'ㄴ', 'ㄵ', 'ㄶ', 'ㄷ', 'ㄹ', 'ㄺ', 'ㄻ', 'ㄼ', 'ㄽ', 'ㄾ', 'ㄿ', 'ㅀ', 'ㅁ', 'ㅂ', 'ㅄ', 'ㅅ', 'ㅆ', 'ㅇ', 'ㅈ', 'ㅊ', 'ㅋ', 'ㅌ', 'ㅍ', 'ㅎ']

def convert(test_keyword):
    split_keyword_list = list(test_keyword)
    #print(split_keyword_list)

    result = list()
    for keyword in split_keyword_list:
        # 한글 여부 check 후 분리
        if re.match('.*[ㄱ-ㅎㅏ-ㅣ가-힣]+.*', keyword) is not None:
            char_code = ord(keyword) - BASE_CODE
            char1 = int(char_code / CHOSUNG)
            result.append(CHOSUNG_LIST[char1])
            #print('초성 : {}'.format(CHOSUNG_LIST[char1]))
            char2 = int((char_code - (CHOSUNG * char1)) / JUNGSUNG)
            result.append(JUNGSUNG_LIST[char2])
            #print('중성 : {}'.format(JUNGSUNG_LIST[char2]))
            char3 = int((char_code - (CHOSUNG * char1) - (JUNGSUNG * char2)))
            if char3 == 0:
                result.append(' ')
            else:
                result.append(JONGSUNG_LIST[char3])
            #print('종성 : {}'.format(JONGSUNG_LIST[char3]))
        else:
            result.append(keyword)
    # result
    
    char_list = result[3:]
    
    char_string = ""
    for i in range(len(char_list)): 
        char_string += char_list[i]
    
    return char_string


def name_preprocessing(dataframe):
    
    dataframe["name_split"] = dataframe["Name"].apply(convert)
    
    for i in range(0, 6):
        for j in range(1, 7):
            if i < j-1:
                dataframe["s_{0}_{1}".format(i,j)] = dataframe["name_split"].apply(lambda x: x[i:j])
                
    dataframe2 = dataframe.drop(columns = ["Name", "Gender", "name_split"])
    
    c = dataframe2.columns[dataframe2.dtypes == object]
    
    #print(dataframe2)
    for i in c:
        dataframe2[i] = le.fit_transform(dataframe2[i])
        
    return dataframe2


def proba_to_index(proba):
    
    if proba > 0.6:
        return 2
    elif proba < 0.4:
        return 1
    else:
        return 0
    
def proba_to_string(proba):
    
    if proba > 0.6:
        return "여성"
    elif proba < 0.4:
        return "남성"
    else:
        return "중성적 이름"
    

def get_data_display(all_data_list):
    data_num = 0
    woman_num = 0
    man_num = 0
    neutral_num = 0
    neutral_list = []
    
    for data_list in all_data_list:
        data_num += 1 
        if data_list[1] == "남성":
            man_num += 1
        elif data_list[1] == "여성":
            woman_num += 1
        else:
            neutral_list.append(data_list[0])
            neutral_num += 1
    
    man_proba = round(100 * (man_num / (man_num + woman_num)), 2)
    woman_proba = round(100 * (woman_num / (man_num + woman_num)), 2)

    return data_num, man_proba, woman_proba, neutral_num, neutral_list


def get_data_test(all_data_list):
    data_num = 0
    correct_num = 0
    neutral = 0
    neutral_list = []
    for data_list in all_data_list:
        data_num += 1 
        if data_list[1] == data_list[2]:
            correct_num += 1
        if data_list[2] == 0:
            neutral_list.append(data_list[0])
            neutral += 1
    
    proba = 100 * (correct_num / data_num)
    
    return proba, data_num, neutral, neutral_list

    
if __name__ == '__main__':
    
    le = LabelEncoder()
    train = pd.read_csv("C:/Users/wowon/Desktop/data/name_train.csv", encoding='cp949') # engine='python')
    #test = pd.read_csv("C:/Users/wowon/Desktop/data/name_test.csv",   encoding='cp949') # engine='python')
    
    name_input = input("각 이름은 쉼표(,)로 구분하세요.\n")
    name_list_not_strip = name_input.split(",")
    name_list = []
    for name in name_list_not_strip:
        name_list.append(name.strip())
    test = pd.DataFrame({ "Name": name_list})
    
    sub = test
    
    all_data = pd.concat([train, test])
    all_data2 = name_preprocessing(all_data)
    
    train2 = all_data2[:len(train)]
    test2 = all_data2[len(train):]
    
    print("")
    print("분석 시작!!")
    print("")
    
    cbc = CatBoostClassifier(verbose = 100)
    cbc.fit(train2, train["Gender"])
    result = cbc.predict_proba(test2)
    
    sub["Implied"] = 0
    sub["Implied"] = result[:,1]
    sub["Implied"] = sub["Implied"].apply(proba_to_string)
    #sub["Implied"] = sub["Implied"].apply(proba_to_index)

    print("")
    print("분석 완료!!")
    print("")

    all_data_list = sub.values.tolist()
    data_num, man_proba, woman_proba, neutral_num, neutral_list = get_data_display(all_data_list)
    print(sub)
    print("총 {0}명을 분석하였으며, 남성 비율은 {1}%이며, 여성 비율은 {2}%입니다.".format(data_num, man_proba, woman_proba))
    #print("(추가 분석) 중성적 이름을 가진 사람은 {0}명이며 리스트는 아래와 같습니다.".format(neutral_num))
    #print(neutral_list)
    
    
    # 여기는 정확도 검사를 위한 데이터 Name과 Gender가 둘 다 있어야함.
    #all_data_list = sub.values.tolist()
    #proba, data_num, neutral, neutral_list = get_data_test(all_data_list)
    #print("{1}의 데이터 중, {0}%를 맞추었습니다. 중성 이름을 가진 이름은 아래의 {2}개입니다. ".format(proba, data_num, neutral))
    #print(neutral_list)
    


# In[2]:


sub


# In[ ]:


#김윤환, 김진중, 강택영, 유지영, 장승린, 심창우, 조중현, 김유라, 이민숙, 김경신, 유준석, 이재원, 송승원, 배인해, 이상은


# In[4]:


pd.Series(cbc.feature_importances_, index = train2.columns).sort_values(ascending = False)


# In[5]:


# s_4_6과 s_3_6과 s_3_5가 가장 영향력이 높았다.

#ㅇㅣ ㅈㅐ ㅇㅝㄴ"
# ㅝㄴ -> s_4_6
# ㅇㄴ -> s_3_6
# ㅇㅝ -> s_3_5


# In[ ]:




