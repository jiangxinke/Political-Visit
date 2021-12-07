'''
把没有官员分类的excel--zhb的excel分类
'''


import pandas as pd
import numpy as np

data_1 = pd.read_excel("访问情况.xlsx")
data_1.head()

data_2 = []
# data_2 = pd.DataFrame(columns=('number','name', 'time', 'class_govern'))
length_data_1 = len(data_1)
all_len = length_data_1
for i in range(length_data_1):
    row = data_1.iloc[[i]].dropna(axis=1)
    row_num = int((row.size - 2)/3)
    for j in range(row_num):
        if row.loc[i][4+j*3] == '正国级':
            class_govern = 1
        if row.loc[i][4+j*3] == '副国级':
            class_govern = 2
        if row.loc[i][4+j*3] == '正省部级':
            class_govern = 3
        if row.loc[i][4+j*3] == '副省部级':
            class_govern = 4
        name = row.loc[i][3+j*3]
        time = row.loc[i][2+j*3]
        # new_data = [{'number':row.loc[i][0],'name':row.loc[i][1], 'time':time, 'class_govern':class_govern}]
        # print(new_data)
        new_data = [row.loc[i][0],row.loc[i][1], time, class_govern,name]

        data_2.append(new_data)
        # data_1.loc['all_len'] = new_data
    # print(row_num)
data_3 = pd.DataFrame(data_2)
data_3.to_csv("Process_Data_5_tuple.csv")
