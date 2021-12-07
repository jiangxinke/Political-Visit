'''
主算法，跑lstm和cpam
'''

import tushare as ts
import numpy as np
import pandas as pd
import datetime
from datetime import timedelta, date
from predict import CPAM

import warnings

warnings.filterwarnings('ignore')

sh_a_df = pd.read_csv("sh_A.csv")  # 上证指数

# 设置token
token = '6acaa6d1a6872945fba43e7418f7b9f47d2eee0ab1aeaf63b5ec3ec3'
ts.set_token(token)
pro = ts.pro_api()

# 读取df
df = pd.read_csv("Process_Data_5_tuple.csv")
df_company_class = pd.read_excel("上证公司数据.xlsx")
# 设置窗口获取时间--> 到访前窗口[before_window,date], 到访后窗口[date,after_window],收集的数据窗口[time_from,before_window]
before_window = 35
after_window = 180
# time_from = 160
before_limit = 20 + 1
after_limit = 30
print("公司数量为：", len(df))
df_array = np.array(df)


# print(df_array)
# 得到AR的累计值
def get_ar_sum(list):
    ar_sum_list = []
    tmp = 0
    for i in range(len(list)):
        tmp += list[i]
        ar_sum_list.append(tmp)
    return ar_sum_list


def match_index(df, choice):
    # choice 表示不排序，为-1代表逆序，为1代表正序
    df["index_pct_chg"] = 0.0000
    df["number"] = 0
    # if(choice==1):
    #     print("长度是：",df.shape[0])
    for i in range(0, df.shape[0]):
        # if(choice==1):
        #     print(i)
        if (choice == -1):
            # print("111")
            df["number"][i] = -i
        if (choice == 1):
            df["number"][i] = i + 1
            # print(df["number"][i])
        temp = df['trade_date'][i]

        if (1 <= int(temp[4:6]) <= 9):
            temp3 = temp[5:6]
        else:
            temp3 = temp[4:6]
        if (1 <= int(temp[6:8]) <= 9):
            temp4 = temp[7:8]
        else:
            temp4 = temp[6:8]
        df['trade_date'][i] = temp[:4] + '-' + temp3 + '-' + temp4
        # print(df['trade_date'][i])
        temp2 = df['trade_date'][i]
        # if (choice == 1):
        #     print("temp2是：", temp2)
        df["index_pct_chg"][i] = sh_a_df.iloc[sh_a_df[sh_a_df.date == temp2].index.tolist()[0]]["pct_chg"]
        # if (choice == 1):
        #     print("index是：",df["index_pct_chg"][i])
    if (choice == 1):
        # print(df)
        pass
    return df


def main(time_from):
    iter = 0  # 轮数
    effective_company = 0  # 有效的公司数量
    AR_LIST = [0 for i in range(before_limit + after_limit)]
    for item in df_array:
        print("This is iter:", iter)
        iter += 1
        # print(item)
        date = item[3]
        date_to = datetime.date(*map(int, date.split('-')))  # 官员的到访时间
        date_end = date_to + timedelta(days=after_window)  # 官员的到访时间=>after_window
        date_before = date_to + timedelta(days=-before_window)  # before_window=>官员的到访时间
        date_earlist = date_to + timedelta(days=-time_from)  # 历史数据开始时间
        date_to_str = str(date_to).replace('-', '')
        date_end_str = str(date_end).replace('-', '')
        date_before_str = str(date_before).replace('-', '')
        date_earlist_str = str(date_earlist).replace('-', '')
        code = item[1]  # 股票代码

        try:

            # 验证的数据集
            date_set = pro.daily(ts_code=code, start_date=date_earlist_str, end_date=date_before_str)

            # 添加指数
            date_set = match_index(date_set, 0)
            # print(date_set['pct_chg'])

            # 第一个窗口
            window_before_set = pro.daily(ts_code=code, end_date=date_to_str, limit=before_limit)

            # print(date_to_str)
            # print(window_before_set)
            # 添加指数
            window_before_set = match_index(window_before_set, -1)
            #

            # 第二个窗口
            # print("end_date:",date_end_str)
            window_after_set = pro.daily(ts_code=code, start_date=date_to_str, end_date=date_end_str).iloc[::-1]
            window_after_set = (window_after_set[1:after_limit + 1]).reset_index()
            new_df = window_after_set

            # 添加指数
            window_after_set = match_index(new_df, 1)

            # print(window_after_set)

            # 用来预测两个窗口的值:
            window_before_set_predict, window_after_set_predict = CPAM(str(date_earlist), str(date_before),
                                                                       str(date_to), str(date_end), date_set,
                                                                       window_before_set, window_after_set)
            ar_df = pd.concat([window_before_set_predict, window_after_set_predict])

            ar_df["ar"] = ar_df['pct_chg'] - ar_df['predict']
            # print(ar_df)
            ar_df = ar_df.sort_values("number")
            # print(ar_df)

            # 新增的
            # 获取CAR0 CAR[-1,1],CAR[-5,5],CAR[-10,10],CAR[-15,15],CAR[-20,20]
            try:  # 要小于before_limit和after_limit
                CAR_0 = np.array(ar_df.loc[ar_df['number'] == 0])[0][-1]
                # print(CAR_0)
                # CAR_1
                CAR_1 = 0
                for i in range(-1, 1 + 1, 1):
                    CAR_1 += np.array(ar_df.loc[ar_df['number'] == i])[0][-1]
                CAR_5 = 0
                for i in range(-5, 5 + 1, 1):
                    CAR_5 += np.array(ar_df.loc[ar_df['number'] == i])[0][-1]
                CAR_10 = 0
                for i in range(-10, 10 + 1, 1):
                    CAR_10 += np.array(ar_df.loc[ar_df['number'] == i])[0][-1]
                CAR_15 = 0
                for i in range(-15, 15 + 1, 1):
                    CAR_15 += np.array(ar_df.loc[ar_df['number'] == i])[0][-1]
                CAR_20 = 0
                for i in range(-20, 20 + 1, 1):
                    CAR_20 += np.array(ar_df.loc[ar_df['number'] == i])[0][-1]
                # print(CAR_0,CAR_20)
            except:
                pass
            ##

            # print(ar_df)
            if (len(ar_df) == len(AR_LIST)):
                for i in range(before_limit + after_limit):
                    AR_LIST[i] += ar_df.iloc[i, -1]
                # AR_LIST += ar_df["ar"]  # 加到AR_LIST里面去
                # print(AR_LIST)
                effective_company += 1
            else:
                pass
            # 新增： 存入CSV中
            company_class = np.array(df_company_class.loc[df_company_class['股票代码'] == code])[0][2]
            market_value_total = np.array(df_company_class.loc[df_company_class['股票代码'] == code])[0][0]
            reg_capital = np.array(df_company_class.loc[df_company_class['股票代码'] == code])[0][5]
            setup_date = np.array(df_company_class.loc[df_company_class['股票代码'] == code])[0][6]
            province = np.array(df_company_class.loc[df_company_class['股票代码'] == code])[0][7]
            employees = np.array(df_company_class.loc[df_company_class['股票代码'] == code])[0][8]
            index_pct_change = np.array(ar_df.loc[ar_df['number'] == 0])[0][-4]
            try:
                # print("111")
                if effective_company == 1:
                    data = [[code, item[2], company_class, market_value_total, item[3], item[4], item[5], reg_capital,
                             setup_date, province, employees, CAR_0, CAR_1, CAR_5, CAR_10, CAR_15, CAR_20,
                             index_pct_change]]
                    car_df = pd.DataFrame(data,
                                          columns=['Stock code', 'Stock Name', 'Industry', 'Total Market Value', 'Date',
                                                   'Governer Class', 'Governer Name',
                                                   'reg_capital', 'setup_date', 'province', 'employees_num',
                                                   'CAR0', 'CAR[-1,1]', 'CAR[-5,5]', 'CAR[-10,10]', 'CAR[-15,15]',
                                                   'CAR[-20,20]', 'index_pct_chg'
                                                   ])  # 将第一维度数据转为为行，第二维度数据转化为列，即 3 行 2 列，并设置列标签

                else:
                    data = [code, item[2], company_class, market_value_total, item[3], item[4], item[5], reg_capital,
                            setup_date, province, employees, CAR_0, CAR_1, CAR_5, CAR_10, CAR_15, CAR_20,
                            index_pct_change]  # 数据
                    car_df.loc[len(car_df)] = data

                # print(car_df)
            except:
                ##
                pass
        except:
            pass
    ## 新增的
    car_df.to_csv("CAR_INDEXS_ALL_company.csv")  # 把数据存入其他csv里面去
    ##
    return AR_LIST, effective_company


def AR_SUM_DRAW(AR_LIST, effective_company):
    # print(AR_LIST, effective_company)
    AR_LIST = np.array(AR_LIST)
    AR_LIST_MEAN = AR_LIST / effective_company
    # AR_LIST_MEAN_df = pd.dataframe(AR_LIST_MEAN)

    print("有效公司数量:", effective_company)
    AR_LIST_MEAN_SUM = get_ar_sum(np.array(AR_LIST_MEAN))

    AR_LIST_MEAN_SUM_df = pd.DataFrame(columns=['mean_AR_sum'], data=AR_LIST_MEAN_SUM)
    AR_LIST_MEAN_SUM_df.to_csv("AR_mean_sum.csv")

    print("AR_均值求和:", AR_LIST_MEAN_SUM)
    import matplotlib.pyplot as plt

    input_values = AR_LIST_MEAN_SUM
    squares = [i for i in range(-before_limit, after_limit, 1)]
    plt.plot(squares, input_values, linewidth=2)
    # 设置图标标题，并给坐标轴加上标签
    plt.title("CAR-Time" + str(time_from) + '-' + str(before_window), fontsize=24)
    plt.xlabel("Days from now", fontsize=14)
    plt.ylabel("CAR", fontsize=14)
    plt.savefig("CAR-Time.png")
    plt.show()


if __name__ == "__main__":
    for time_from in range(300,310):
        print("this is time:",time_from)
        AR_LIST, effective_company = main(time_from)
        AR_SUM_DRAW(AR_LIST, effective_company)
