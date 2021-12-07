'''
输入参数：
    - 官员名称即对应的职务表
    - 搜索的关键词，类似 考察 企业|公司
'''
import pandas as pd

gov_name_df = pd.read_csv('gov_name.csv',encoding = 'gb2312')
up_date_df = pd.read_csv('up_time_after.csv',error_bad_lines=False,encoding = 'UTF-8')


first_class_name = gov_name_df['1']
first_date = up_date_df['1']

second_class_name = gov_name_df['2']
second_date = up_date_df['2']

third_class_name = gov_name_df['3']
third_date = up_date_df['3']

first_class_name = first_class_name.dropna()
second_class_name = second_class_name.dropna()
third_class_name = third_class_name.dropna()
first_date = first_date.dropna()
second_date = second_date.dropna()
third_date = third_date.dropna()

search_words_1 = ['考察', '调研']
search_words_2 = ['企业', '公司']

search_words_list = []

def build_search_words_list(class_gov):
    # 按照级别选取
    if class_gov == 1:
        gov_name = first_class_name
        date_up = first_date
    elif class_gov == 2:
        gov_name = second_class_name
        date_up = second_date
    elif class_gov == 3:
        gov_name = third_class_name
        date_up = third_date
    else:
        pass
    # 构建搜索的关键词
    for item in gov_name:
        search_words_list.append(item + '%20' + search_words_1[0] +'|' + search_words_1[1] + '%20' + search_words_2[0] + '|' + search_words_2[1])
    # for i in range(gov_name):
    #     item = gov_name[i]


    return search_words_list,date_up





# search_words_212,list = build_search_words_list(1)
# print(search_words_212)
# print(list)
# # print(type(se))
