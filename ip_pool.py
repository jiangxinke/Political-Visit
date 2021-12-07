def get_ip_pool():
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
        检查代理IP的方法
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

        for page in range(1,5):
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
        print(can_use_all)
        print(len(can_use_all))
        return can_use_all

get_ip_pool()