'''
处理主算法生成的数据
'''

import pandas as pd
import numpy as np
import datetime
import warnings
warnings.filterwarnings('ignore')

df = pd.read_csv("CAR_INDEXS_ALL_company_lstm.csv")
df["delta_days"] = 0
# df = df.dropna()
# 处理这个array
for i in range(len(df)):
    temp = df['setup_date'][i]
    now_date = df['Date'][i]
    # print(now_date)
    strlist = now_date.split('-')
    if len(strlist[1])==1:
        strlist[1] = '0'+strlist[1]
    if len(strlist[2])==1:
        strlist[2] = '0'+strlist[2]
    now_data_str = strlist[0]+strlist[1]+strlist[2]
    # print(now_data_str)
    if np.isnan(temp)==True :
        df['delta_days'][i] = temp     # 加空值
        # print(temp)
        pass
    else:
        # print(temp)
        set_up_data = datetime.datetime.strptime(str(temp)[:-2], "%Y%m%d")
        # print(set_up_data)
        now_data = datetime.datetime.strptime(now_data_str, "%Y%m%d")
        # print(set_up_data,now_data)
        diff_days = (now_data - set_up_data).days
        # print(diff_days)
        df['delta_days'][i] = diff_days
df.fillna(df.mean())
# print(df)
df['reg_capital'].fillna(df['reg_capital'].mean(),inplace = True)
df['employees_num'].fillna(int(df['employees_num'].mean()),inplace = True)
df['delta_days'].fillna(int(df['delta_days'].mean()),inplace = True)
df.to_csv("Multi_Logit2.csv")