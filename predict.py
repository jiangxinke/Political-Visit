'''
CPAM,LSTM预测算法
'''
# # 测试，使用均值predict
#
# def predict(array,length):
#     array_mean = array.mean()
#     array = []
#     for i in range(length):
#         array.append(array_mean)
#     return array

def CPAM(date_earlist,date_before,date_to,date_end,date_set,window_before_set,window_after_set):
    import tushare as ts
    import numpy as np
    import pandas as pd
    import statsmodels.api as sm
    # 无风险收益率
    rf = 1.0385 ** (1 / 365) - 1
    Return = date_set[['pct_chg','index_pct_chg']]
    # print(Return)
    Eret = Return - rf
    # # 拟合CAPM模型
    model = sm.OLS(Eret.pct_chg[1:], sm.add_constant(Eret.index_pct_chg[1:]))
    result = model.fit()
    # print(result.summary())
    # 然后用window_before_set,date_before,date_to 得到 window_before_predict
    Premydf = window_before_set.index_pct_chg - rf
    ActualZGLT_before= result.params[0]+result.params[1]*Premydf # 预测的
    window_before_set["predict"] = ActualZGLT_before + rf

    # 然后用window_after_set,date_to,date_end 得到 window_after_predict
    # 后窗口拟合结果
    Premydf =window_after_set.index_pct_chg - rf
    ActualZGLT_after = result.params[0] + result.params[1] * Premydf  # 预测的
    window_after_set["predict"] = ActualZGLT_after + rf

    return window_before_set,window_after_set

def CPAM_predict(code,date_earlist_str,date_before_str,date_to_str,date_end_str):
    import tushare as ts
    import numpy as np
    import pandas as pd
    import statsmodels.api as sm
    mydf = ts.get_hist_data('sh', ktype='W', start=date_earlist_str, end=date_before_str)

    ZGLT = ts.get_hist_data(code=code, ktype='W', start=date_earlist_str, end=date_before_str)
    print(ZGLT.p_change)    # ZGLT 是y
    # print(len(mydf), len(ZGLT))
    # 无风险收益率
    rf = 1.0385 ** (1 / 365) - 1
    Return = pd.merge(pd.DataFrame(mydf.p_change), pd.DataFrame(ZGLT.p_change), left_index=True, right_index=True,
                      how='inner')
    print(Return)
    Eret = Return - rf
    # print(Eret)
    # 拟合CAPM模型
    model = sm.OLS(Eret.p_change_y[1:], sm.add_constant(Eret.p_change_x[1:]))
    result = model.fit()
    # print(result.summary())
    # 根据拟合结果计算预期收益率
    # 前窗口拟合结果：
    mydf_before = ts.get_hist_data('sh', ktype='W', start=date_before_str, end=date_to_str)
    Premydf = mydf_before.p_change - rf
    ActualZGLT_before= result.params[0]+result.params[1]*Premydf # 预测的
    return_before = np.array(ActualZGLT_before.reindex(index=ActualZGLT_before.index[::-1]))

    # 后窗口拟合结果
    mydf_after = ts.get_hist_data('sh', ktype='W', start=date_to_str, end=date_end_str)
    Premydf = mydf_after.p_change - rf
    ActualZGLT_after = result.params[0] + result.params[1] * Premydf  # 预测的
    return_after = np.array(ActualZGLT_after.reindex(index=ActualZGLT_after.index[::-1]))

    return return_before,return_after

# CPAM_predict('600566.SH'[0:6],'2016-01-01','2017-01-01','2017-01-30','2017-02-20')

