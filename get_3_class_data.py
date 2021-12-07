# %%
import time
import datetime
from datetime import datetime as d
import requests
from lxml import etree
from newspaper import Article
from newspaper.configuration import Configuration
import pandas as pd
from act_py.searchWordsBuild import build_search_words_list
# proxy_id = 1   #全局变量，如果当前ip无法用，就更换到下一个取
import pytz
utc=pytz.UTC

def find_news_nums_page(tree):
    '''
    这个函数的目的是寻找到新闻界面一共有多少条新闻
    :param tree:
    :return:
    '''
    elements = []
    # 寻找xpath路径
    xpath_path = '//*[@id="content_left"]/div[2]/div[@class="result-op c-container xpath-log new-pmd"]'
    elements.append(tree.xpath(xpath_path))
    # print(elements[0])
    #     print(len(elements[0]))
    return len(elements[0])  # 返回新闻数目如10，9

def extract_by_newspaper(url1,filename,search_word_i,ip_pool_all,up_date,gov_name_i, page_num = 501):
    '''
    首先构建IP池，然后挖掘出新闻来，存入CSV中
    :param url1:
    :param url3:
    :param filename:
    :param search_word_i:
    :param ip_pool_all:
    :param page_num:
    :return:
    '''
    proxy_id = 1  # 全局变量，如果当前ip无法用，就更换到下一个取
    # 构建IP池
    print(ip_pool_all)
    # ip池的长度
    ip_pool_len = len(ip_pool_all)
    print(ip_pool_len)  # 此时ip池的大小
    ip_proxy_now = ip_pool_all[proxy_id][0]
    # 在newspaper中构建config，然后再跑
    config = Configuration()
    config.proxies = ip_proxy_now

    # 构建url
    for url_2 in range(1, page_num):
        print("----This is page", url_2)
        url = url_1 + str(url_2*10)
        print(url)
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36 Edg/94.0.992.31'}
        page_text_return = requests.get(url=url,headers=headers)
        # print(page_text_return.status_code)
        page_text = page_text_return.text
        # print(page_text)
        tree = etree.HTML(page_text)
        # print(tree)

        urls = []
        news_num = find_news_nums_page(tree)
        print("Now nums of news is ", news_num)

        for i in range(1, news_num):  # news_num为10，从1~10
            #         print(i) //*[@id="1"]/div/h3/a
            xpath_path = '//*[@id="'+str(i)+'"]/div/h3/a/@href'
            # 将这一页的每一条新闻存入到urls中，方便newspaper提取
            # print("tree.xpath(xpath_path)")
            urls.append(tree.xpath(xpath_path))
        # print(urls)
        news_title = []
        news_text = []
        news_time = []
        news_name = []
        # 此时已经获取了一页的url
        for item in urls:
            if len(item)==0:
                pass
            else:
                print(item[0])
                url_item = item[0]
                try:
                    # newspaper提取
                    paper = Article(url_item, language='zh', memoize_articles=False, config=config)
                    paper.download()
                    paper.parse()
                except Exception as e:
                    # 如果不行的话，就更换ip池  ip_proxy_now = ip_pool_all[proxy_id][0]
                    print(e)
                    while(True):
                        proxy_id = (proxy_id+1)%ip_pool_len   # 更换ip池，+1
                        ip_proxy_now = ip_pool_all[proxy_id][0]
                        try:
                            config = Configuration()
                            config.proxies = ip_proxy_now
                            paper = Article(url_item, language='zh', memoize_articles=False, config=config)
                            break
                        except:
                            proxy_id = (proxy_id+1)%ip_pool_len   # 更换ip池，+1
                            ip_proxy_now = ip_pool_all[proxy_id][0]
                            break
                            pass
                    pass
            # print(type(paper.publish_date))
                try:
                    if (isinstance(paper.publish_date, datetime.datetime) == True) and (paper.publish_date).replace(tzinfo=utc) >= (d.strptime(up_date, "%Y-%m-%d")).replace(tzinfo=utc):     # 要求官员的上任日期xxx
                        # 将数据存入进去
                        news_title.append(paper.title)
                        news_time.append(paper.publish_date)
                        news_text.append(paper.text)
                        news_name.append(gov_name_i)
                        # print(1111)
                        print(paper.title)
                    #         print(paper.publish_date)
                    #         print(paper.text)
                    else:
                        pass
                except:
                    pass

        # 转换为dateframe格式
        paper_data = pd.DataFrame({'title': news_title,'gov_name':gov_name_i, 'time': news_time, 'text': news_text})
        # print(paper_data)
        # 存入文件中
        if url_2 == 1 and search_word_i == 0 :
            paper_data.to_csv(filename)  # 相对位置，保存在getwcd()获得的路径下
        else:
            paper_data.to_csv(filename, mode='a', header=False)
            print("已存入",filename)

def get_ip_pool(page_pool):
    '''
    构建IP地址池
    :return:
    '''
    import requests
    import parsel

    def send_request(page):
        print("=====正在抓取第",page,"页=====")
        '''
        发送请求，获取响应数据的方法
        :return:
        '''
        # 1. 确定headers数据
        base_url = 'https://www.kuaidaili.com/free/inha/'+str(page)+"/"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36 Edg/94.0.992.31'}

        # 2. 发送请求
        response = requests.get(base_url,headers=headers)
        data = response.text
        # with open("kuaidaili.html",'wb') as f:
        #     f.write(data)
        return data

    def parse_data(data):
        # 3. 解析数据
        ## 数据转换
        html_data = parsel.Selector(data)
        ## 解析数据
        paser_list = html_data.xpath('//table[@class="table table-bordered table-striped"]/tbody/tr')
        # print(paser_list)
        return paser_list

    def check_ip(proxies_list):
        '''
        检查代理IP的方法，检查IP是否生效
        :return:
        '''
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36 Edg/94.0.992.31'}
        can_use_ip = []
        for proxies in proxies_list:
            try:
                response = requests.get('https://www.baidu.com/',headers=headers,proxies=proxies,timeout=1)
                if response.status_code == 200:
                    can_use_ip.append(proxies)
            except Exception as e:
                # print(e)
                pass
        # print(can_use_ip)
        return can_use_ip


    if __name__ == '__main__':
        proxies_list = []

        for page in range(1,page_pool):
            data = send_request(page)
            proxies_list = parse_data(data)
            # print(len(proxies_list))
            # {"协议类型":"ip"；”端口“}
            can_use_all = []
            for i in range(1,15):
                tr = proxies_list[i]
                proxies_dict = {}
                # http_type = tr.xpath('./td[4]/text()').extract_first()
                ip_num = tr.xpath('./td[1]/text()').extract_first()
                port_num = tr.xpath('./td[2]/text()').extract_first()

                proxies_dict['HTTP'] = ip_num + ":" + port_num
                proxies_list.append(proxies_dict)
                # print(proxies_dict)
                can_use_all.append(check_ip(proxies_list))
                # print(can_use)
                # print(len(can_use))
        print("====当前可用的地址池如下====")
        print(can_use_all)
        # print(len(can_use_all))
        # 返回可用的地址池列表：格式如：[[{'HTTP': '111.225.153.79:3256'}], [{'HTTP': '111.225.153.79:3256'}, {'HTTP': '27.191.60.228:3256'}], [{'HTTP': '111.225.153.79:3256'}, {'HTTP': '27.191.60.228:3256'}, {'HTTP': '123.171.42.212:3256'}], [{'HTTP': '111.225.153.79:3256'}, {'HTTP': '27.191.60.228:3256'}, {'HTTP': '123.171.42.212:3256'}, {'HTTP': '60.167.102.105:1133'}], [{'HTTP': '111.225.153.79:3256'}, {'HTTP': '27.191.60.228:3256'}, {'HTTP': '123.171.42.212:3256'}, {'HTTP': '60.167.102.105:1133'}, {'HTTP': '117.35.253.9:3000'}], [{'HTTP': '111.225.153.79:3256'}, {'HTTP': '27.191.60.228:3256'}, {'HTTP': '123.171.42.212:3256'}, {'HTTP': '60.167.102.105:1133'}, {'HTTP': '117.35.253.9:3000'}, {'HTTP': '60.167.135.121:1133'}], [{'HTTP': '111.225.153.79:3256'}, {'HTTP': '27.191.60.228:3256'}, {'HTTP': '123.171.42.212:3256'}, {'HTTP': '60.167.102.105:1133'}, {'HTTP': '117.35.253.9:3000'}, {'HTTP': '60.167.135.121:1133'}, {'HTTP': '117.68.195.240:1133'}], [{'HTTP': '111.225.153.79:3256'}, {'HTTP': '27.191.60.228:3256'}, {'HTTP': '123.171.42.212:3256'}, {'HTTP': '60.167.102.105:1133'}, {'HTTP': '117.35.253.9:3000'}, {'HTTP': '60.167.135.121:1133'}, {'HTTP': '117.68.195.240:1133'}, {'HTTP': '118.117.188.156:3256'}], [{'HTTP': '111.225.153.79:3256'}, {'HTTP': '27.191.60.228:3256'}, {'HTTP': '123.171.42.212:3256'}, {'HTTP': '60.167.102.105:1133'}, {'HTTP': '117.35.253.9:3000'}, {'HTTP': '60.167.135.121:1133'}, {'HTTP': '117.68.195.240:1133'}, {'HTTP': '118.117.188.156:3256'}, {'HTTP': '123.171.42.202:3256'}], [{'HTTP': '111.225.153.79:3256'}, {'HTTP': '27.191.60.228:3256'}, {'HTTP': '123.171.42.212:3256'}, {'HTTP': '60.167.102.105:1133'}, {'HTTP': '117.35.253.9:3000'}, {'HTTP': '60.167.135.121:1133'}, {'HTTP': '117.68.195.240:1133'}, {'HTTP': '118.117.188.156:3256'}, {'HTTP': '123.171.42.202:3256'}, {'HTTP': '182.84.145.121:3256'}], [{'HTTP': '111.225.153.79:3256'}, {'HTTP': '27.191.60.228:3256'}, {'HTTP': '123.171.42.212:3256'}, {'HTTP': '60.167.102.105:1133'}, {'HTTP': '117.35.253.9:3000'}, {'HTTP': '60.167.135.121:1133'}, {'HTTP': '117.68.195.240:1133'}, {'HTTP': '118.117.188.156:3256'}, {'HTTP': '123.171.42.202:3256'}, {'HTTP': '182.84.145.121:3256'}, {'HTTP': '163.125.249.83:8118'}], [{'HTTP': '111.225.153.79:3256'}, {'HTTP': '27.191.60.228:3256'}, {'HTTP': '123.171.42.212:3256'}, {'HTTP': '60.167.102.105:1133'}, {'HTTP': '117.35.253.9:3000'}, {'HTTP': '60.167.135.121:1133'}, {'HTTP': '117.68.195.240:1133'}, {'HTTP': '118.117.188.156:3256'}, {'HTTP': '123.171.42.202:3256'}, {'HTTP': '182.84.145.121:3256'}, {'HTTP': '163.125.249.83:8118'}, {'HTTP': '111.72.25.108:3256'}], [{'HTTP': '111.225.153.79:3256'}, {'HTTP': '27.191.60.228:3256'}, {'HTTP': '123.171.42.212:3256'}, {'HTTP': '60.167.102.105:1133'}, {'HTTP': '117.35.253.9:3000'}, {'HTTP': '60.167.135.121:1133'}, {'HTTP': '117.68.195.240:1133'}, {'HTTP': '118.117.188.156:3256'}, {'HTTP': '123.171.42.202:3256'}, {'HTTP': '182.84.145.121:3256'}, {'HTTP': '163.125.249.83:8118'}, {'HTTP': '111.72.25.108:3256'}, {'HTTP': '163.125.249.29:8118'}], [{'HTTP': '111.225.153.79:3256'}, {'HTTP': '27.191.60.228:3256'}, {'HTTP': '123.171.42.212:3256'}, {'HTTP': '60.167.102.105:1133'}, {'HTTP': '117.35.253.9:3000'}, {'HTTP': '60.167.135.121:1133'}, {'HTTP': '117.68.195.240:1133'}, {'HTTP': '118.117.188.156:3256'}, {'HTTP': '123.171.42.202:3256'}, {'HTTP': '182.84.145.121:3256'}, {'HTTP': '163.125.249.83:8118'}, {'HTTP': '111.72.25.108:3256'}, {'HTTP': '163.125.249.29:8118'}, {'HTTP': '182.84.144.167:3256'}]]
        return can_use_all

def get_page_num(url):
    '''
    寻找到当前链接一共有多少个页面，如果大于20页就取20页，否则就取当前页数（floor）--保守
    :param url:
    :return:
    '''
    import parsel
    import requests
    import math

    # 网址--靠传入的网址计算
    # url = 'http://search.youth.cn/cse/search?q=%E4%B9%A0%E8%BF%91%E5%B9%B3%E8%80%83%E5%AF%9F%E4%BC%81%E4%B8%9A&click=1&entry=1&s=15107678543080134641&nsid='
    # 保守估计，一页12个
    news_num_for_one_page = 12
    # num_page = 0
    # 构建header
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36 Edg/94.0.992.31'}
    response = news_all = requests.get(url, headers=headers)
    # data = response.text.encode("iso-8859-1").decode('UTF-8')
    data = response.text
    html_data = parsel.Selector(data)
    paser_list = html_data.xpath('//*[@id="header_top_bar"]/span/text()').extract_first()
    ## 已经找到了需要的关键信息
    # print(paser_list)
    if paser_list == None or len(paser_list)==0:
        return 0
    else:
        # 把关键信息的汉字去掉
        num_all = int(''.join([x for x in paser_list if x.isdigit()]))
        page_num_num = math.floor(num_all/news_num_for_one_page)
        print("====当前新闻一共有：",page_num_num,'页====')
        # 如果不足20页按照当前页面算，如果大于20页就按20页计算
        return min(page_num_num,20)

if __name__ == '__main__':
    ## 构建proxis IP池：
    page_pool = 2 # 这个是要抓取多少也ip池，一般为5
    ip_pool_all = get_ip_pool(page_pool)
    # print(ip_pool_all)

    # for循环第一级：是官员的级别排名从1-2-3
        # for循环第二级：是每个官员级别的名字--然后按照这个级别的名字搜索
    # for class_gov in [1,2,3]:
    for class_gov in [2]:
        print("This is the",class_gov,"class")   # 第几级别
        words,date_list = build_search_words_list(class_gov)  # 在searchWordsBuild中，构建搜索的关键词
        for i in range(len(words)):
            print("This is the ",i," search words:",words[i])  # 这一级别的第几个官员

            '''
            百度搜索要改
            百度搜索是： 0 ，10， 20， 30， 40， 50... 每10个一页

            '''
            # 构建搜索网页，然后进行搜索界面
            url_1 = 'https://www.baidu.com/s?ie=utf-8&medium=0&rtt=1&bsst=1&rsv_dl=news_b_pn&cl=2&wd=' + words[i] +'&tn=news&rsv_bp=1&rsv_sug3=12&rsv_sug1=1&rsv_sug7=100&rsv_n=2&oq=&rsv_sug2=0&rsv_btype=t&f=8&inputT=7740&rsv_sug4=7771&x_bfe_rqs=03E80&x_bfe_tjscore=0.100000&tngroupname=organic_news&newVideo=12&goods_entry_switch=1&pn='

            '''
            百度搜索要改
            '''
            page_num = get_page_num(url_1+str(0))  # 搜索的页面数目--构建搜索页面数目
            # print(page_num)
            ## 测试
            # page_num = 2

            if page_num == None or page_num == 0:
                pass
            else:
                # 按照级别构建file_name
                filename = str(class_gov)+'_ResultPages.csv'
                # 睡眠60s，怕被和谐了
                print('---------------SLEEP 120 -----------------')
                time.sleep(10)
                print('---------------OVER-----------------------')
                # 得到官员的上任日期：
                up_date = date_list[i] ## 这是要搜索的这个官员的上任日期，做区别区分
                # 挖掘新闻信息并且存入excel中
                extract_by_newspaper(url_1,filename,i,ip_pool_all,up_date,words[i][0:3],page_num)

    print("===============================文本已全部挖掘===================================")


