def extract_company_name(text):
    import os
    from pyltp import NamedEntityRecognizer,Segmentor,Postagger

    LTP_DATA_DIR = "D:/Programs/paper/paper_fin/data_extract/ltp_data/"
    cws_model_path = os.path.join(LTP_DATA_DIR, 'cws.model')  # 分词模型路径，模型名称为`cws.model`
    pos_model_path = os.path.join(LTP_DATA_DIR, 'pos.model')  # 词性标注模型路径，模型名称为`pos.model`
    ner_model_path = os.path.join(LTP_DATA_DIR, 'ner.model')  # 命名实体识别模型路径，模型名称为`pos.model`

    segmentor = Segmentor()  # 初始化实例
    segmentor.load(cws_model_path)  # 加载模型
    postagger = Postagger()  # 初始化实例
    postagger.load(pos_model_path)  # 加载模型
    recognizer = NamedEntityRecognizer()  # 初始化实例
    recognizer.load(ner_model_path)  # 加载模型
    try:
        words = segmentor.segment(text)  # 分词
        # print (' '.join(words))
        segmentor.release()
    except:
        words = []
        pass
    postags = postagger.postag(words)  # 词性标注
    # print (' '.join(postags))
    postagger.release()
    netags = recognizer.recognize(words, postags)  # 命名实体识别
    # print (','.join(netags))
    recognizer.release()
    '''
    refers to : https://ltp.readthedocs.io/zh_CN/latest/appendix.html
    '''
    netags_list = ','.join(netags).split(',')
    # print(netags_list)

    words_list = ','.join(words).split(',')
    # print(words_list)

    company_name = []
    flag = False  # a flag that means there is no Ni exists
    for i in range(len(netags_list)):
        item = netags_list[i]
        if item == 'B-Ni' and flag == False:
            # print(item)
            new_company = ''
            new_company = new_company + words_list[i]
            flag = True
        elif (item =='I-Ni' and flag == True):
            # print(item)
            new_company = new_company + words_list[i]
        elif item =='E-Ni' and flag == True:
            if words_list[i] == '公司' or words_list[i] == '企业' or words_list[i] == '集团' or words_list[i] == '有限公司':
                new_company = new_company + words_list[i]
                flag = False

                if new_company == '公司' or new_company == '集团' or new_company == '有限公司':
                    pass
                else:
                    company_name.append(new_company)
            else:
                new_company = ''
        # elif item == 'S-Ni':
        #     if words_list[i] == '公司' or words_list[i] == '企业' or words_list[i] == '集团' or words_list[i] == '有限公司':
        #         company_name.append(words_list[i])
        #     else:
        #         pass
        else:
            pass
    # print(company_name)
    company_name = list(set(company_name))

    return company_name


# text = "习近平在陕西汽车控股集团有限公司了解企业复工复产情况，同时他前往陕西西北工业有限公司查询业务和北京工业大学和中共中央政治局"
# ans = extract_company_name(text)
# print(ans)


def build_company_name():
    import pandas as pd
    for i in [1,2,3]:
    # for i in [1]:
        filename = str(i) + '_ResultPages.csv'
        csv_file = pd.read_csv(filename)
        filename_after = str(i) + '_CompanyName.csv'

        date_df = csv_file['time']
        text = csv_file['text']
        company_name_after = []

        for item in text:

            company_list_after = extract_company_name(item)
            print(company_list_after)
            company_name_after.append(company_list_after)

        company_name_after_df = pd.DataFrame(company_name_after)
        print(date_df.size==company_name_after_df)
        company_df = pd.concat([date_df,company_name_after_df],axis=1)
        company_df.to_csv(filename_after)

build_company_name()