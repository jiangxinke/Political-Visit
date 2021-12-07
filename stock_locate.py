'''
最早的测试算法
'''

import tushare as ts
import numpy as np
import pandas as pd
import datetime
from datetime import timedelta, date

# 设置token
token= '6acaa6d1a6872945fba43e7418f7b9f47d2eee0ab1aeaf63b5ec3ec3'
ts.set_token(token)
pro=ts.pro_api()

# 读取df
df = pd.read_csv("Process_Data_5_tuple.csv")
df_company_class = pd.read_excel("上证公司数据.xlsx")
# 设置窗口获取时间--20Day
window_date = 15
back_time_start = 40
back_time_end = 10
print(len(df))
df_array = np.array(df)
positive_count = 0
negative_count = 0
iter = 0
delta_pct_chg_list = []

for item in df_array:
    print("This is iter:",iter)
    iter+=1
    # print(item)
    date = item[3]
    date_start = datetime.date(*map(int,date.split('-')))
    # print(type(date_date))
    date_end = date_start + timedelta(days=window_date)
    # print(date_end)
    code = item[1]
    # 获取公司类别
    try:
        company_class = np.array(df_company_class.loc[df_company_class['股票代码']==code])[0][2]
        # 同类别的公司的情况
        company_same_class_list = []
        dff = np.array(df_company_class.loc[df_company_class['所属行业'] == company_class])
        # print(dff)
        # company_same_class_list.append(df_company_class.loc[df_company_class['所属行业']==company_class])
        for item in dff:
            company_same_class_list.append(item[3])
        # print(company_same_class_list)

        date_start_str = str(date_start).replace('-', '')
        date_pas_year_str = str(date_start + timedelta(days=-back_time_start)).replace('-','')
        date_pas_year_end_str = str(date_start + timedelta(days=-back_time_end)).replace('-','')

        # print(date_pas_year_str)

        date_end_str = str(date_end).replace('-', '')
        # print(code)
        # 获取后一段时间的数据
        dfff = pro.daily(ts_code=code, start_date=date_start_str, end_date=date_end_str)
        window_pct_chg = dfff['pct_chg'].mean()
        # 获取后一段时间的行业数据
        class_mean = []
        for coder in company_same_class_list:
            df_class = pro.daily(ts_code=coder, start_date=date_start_str, end_date=date_end_str)
            window_pct_chg_class = df_class['pct_chg'].mean()
            class_mean.append(window_pct_chg_class)
        class_mean = [class_mean_ for class_mean_ in class_mean if
                              class_mean_ == class_mean_]
        delta_market_later = window_pct_chg - sum(class_mean)/len(class_mean)

        ###
        dfffff = pro.daily(ts_code=code, start_date=date_pas_year_str, end_date=date_pas_year_end_str)
        window_pct_chg_before = dfffff['pct_chg'].mean()
        # 获取后一段时间的行业数据
        class_mean_before = []
        for coderr in company_same_class_list:
            df_class_before = pro.daily(ts_code=coderr, start_date=date_start_str, end_date=date_end_str)
            window_pct_chg_class_before = df_class_before['pct_chg'].mean()
            class_mean_before.append(window_pct_chg_class_before)
        class_mean_before = [class_mean_before_ for class_mean_before_ in class_mean_before if
                      class_mean_before_ == class_mean_before_]
        delta_market_before = window_pct_chg_before - sum(class_mean_before) / len(class_mean_before)
        ###

        delta_pct_chg = delta_market_later - delta_market_before
        print(delta_pct_chg)
        if(delta_pct_chg>0):
            positive_count += 1
        if(delta_pct_chg<0):
            negative_count +=1

        delta_pct_chg_list.append(delta_pct_chg)

    except:
        delta_pct_chg_list.append('nan')
        pass
# df = pd.concat([df, pd.DataFrame(columns=delta_pct_chg_list)])
df["pct_delta"] = pd.DataFrame(delta_pct_chg_list)
delta_pct_chg_list = [delta_pct_chg_list_ for delta_pct_chg_list_ in delta_pct_chg_list if delta_pct_chg_list_ == delta_pct_chg_list_]
print("Total:",sum(delta_pct_chg_list)/len(delta_pct_chg_list))
print("Negative:Positive:",negative_count,positive_count)

df.to_csv("Answer_compute.csv")
