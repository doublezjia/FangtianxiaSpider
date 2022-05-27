#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Author  : zealous (doublezjia@163.com)
# @Date    : 2022/5/19
# @Link    : https://github.com/doublezjia
# @Desc    :

import os,requests,sys,csv,time,random,re,json
from bs4 import BeautifulSoup
from datetime import datetime

# 房天下新房页面
base_url = 'https://{city_url_name}.newhouse.fang.com'
# 房天下城市页
area_url = 'https://www.fang.com/SoufunFamily.htm'
# 请求头列表
headers_List = [
    {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36'},
    {'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:60.0) Gecko/20100101 Firefox/60.0'},
    {'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50'},
           ]
# 用来添加csv表头
csv_head = ('城市','房名','类型','地址','销售状态','特色','价格(元/㎡)')


# 房天下爬虫函数
def FangTianXia_Spider(city,city_url_name,url):
    url = url
    city = city
    city_url_name = city_url_name
    headers = headers_List[random.randint(0,len(headers_List)-1)]

    # 获取页面
    req = requests.get(url,headers=headers)
    soup = BeautifulSoup(req.text,'html.parser')
    # 判断是否能正常访问
    if req.status_code == 200:
        print('页面访问正常.')
        try:
            print('获取目标页面信息并保存到CSV表中')
            # 获取目标页面信息
            row = soup.find('div',{'class':'nl_con clearfix'}).find('ul').find_all('li',id=True)
            for i in row:
                name = i.find('div',{'class':'nlcd_name'}).find('a').text.strip()
                House_type = i.find('div',{'class':'house_type clearfix'}).text.strip()
                relative_message = i.find('div',{'class':'relative_message clearfix'}).find('a')['title']
                sale_Status = i.find('div',{'class':'fangyuan'}).find('span').text.strip()

                feature_list = i.find('div',{'class':'fangyuan'}).find_all('a')
                feature = ''
                for fea in feature_list:
                    feature = fea.text.strip() + ' ' + feature

                # 判断价格的div用的class是哪一种类型
                if i.find('div',{'class':'nhouse_price'}) != None:
                    nhouse_price = i.find('div',{'class':'nhouse_price'}).find_all(text=True)[-3].strip()
                else:
                    nhouse_price = i.find('div', {'class': 'kanesf'}).find_all(text=True)[0].strip()

                # 输出信息
               #  msg = """
               #       房名：{name}
               #       类型：{House_type}
               #       地址：{relative_message}
               #    销售状态：{sale_Status}
               #       特色：{feature}
               # 价格(元/㎡)：{nhouse_price}
               #      """.format(name=name,House_type=re.sub(r'\s',"",House_type),\
               #                 relative_message=relative_message,\
               #                 sale_Status=sale_Status,\
               #                 feature=feature.strip().replace(' ','/'),\
               #                 nhouse_price=nhouse_price)
               #  print (msg)

                # 保存到CSV中
                csv_meg = (city,name,re.sub(r'\s',"",House_type),\
                               relative_message,\
                               sale_Status,\
                               feature.strip().replace(' ','/'),\
                               nhouse_price)
                save_csv(csv_meg)

            # 获取页数
            page_row = soup.find('div', {'class': 'page'}).find('ul', {"class": "clearfix"}).find('li', {
                "class": "fr"}).find_all('a')
            # 获取下一页和尾页
            next_page = page_row[-2]
            last_page = page_row[-1]
            Next_Page_URL = base_url.format(city_url_name=city_url_name) + next_page["href"]

            # 记录下一页的url保存到json中，方便中断后再重新爬取
            URL_Message = {
                "city": city,
                "city_url_name": city_url_name,
                "URL": Next_Page_URL,
            }
            with open('spider_url.json','w',encoding = 'utf-8') as f:
                f.write(json.dumps(URL_Message,ensure_ascii=False))

            # 判断是否为最后一页
            if last_page["class"][0] != 'active':
                print('下一页地址是：%s' % Next_Page_URL)
                time_num = random.randint(2, 10)
                print('防止网站禁止爬虫，等待%s秒' % time_num)
                time.sleep(time_num)
                print ('爬取下一页')
                return FangTianXia_Spider(city,city_url_name,Next_Page_URL)
            else:
                sys.exit('这是最后一页了，爬虫结束！！！')

        except AttributeError as a:
            print (a)
            sys.exit('运行出错了，请排查原因！！！！')


# 获取对应城市名的url前缀
def Fangtianxia_city(area_url,city):
    area_url = area_url
    F_city = city
    headers = headers_List[random.randint(0, len(headers_List) - 1)]

    req = requests.get(area_url, headers=headers)
    soup = BeautifulSoup(req.text, 'html.parser')
    # 通过bs4查找获取的网页中是否有该城市名，有就返回网址的url前缀，没有就返回None
    data = soup.find('div',{'id':'c02'}).find('a',text='%s' % F_city)
    if data:
        city_url_name = data['href'].replace('http://','').split('.')[0]
        return city_url_name
    else:
        return None



# 保存csv
def save_csv(msg):
    with open('fangtianxia.csv','a',newline='') as datacsv:
        csvwriter = csv.writer(datacsv,dialect=('excel'))
        csvwriter.writerow(msg)

# 主函数
def main():
    URL_Message = None

    # 判断是否有csv文件，没有则创建，添加表头
    if not os.path.isfile('fangtianxia.csv'):
        with open('fangtianxia.csv', 'w', newline='') as datacsv:
            csvwriter = csv.writer(datacsv, dialect=('excel'))
            csvwriter.writerow(csv_head)

    # 判断json文件是否存在
    if os.path.isfile('spider_url.json'):
        # 读取spider_url.json中的内容
        with open('spider_url.json', 'r',encoding = 'utf-8') as f:
            try:
                URL_Message = json.load(f)
            except json.decoder.JSONDecodeError as j_error:
                print(j_error)
                # 删除csv文件
                if os.path.exists("fangtianxia.csv"):
                    os.remove("fangtianxia.csv")
                sys.exit('读取spider_url.json文件出错，无法继续上次记录，请删除json文件并重新运行!!!')

    # 判断读取到spider_url.json中的内容是否存在
    if URL_Message:
        try:
            city = URL_Message['city']
            city_url_name = URL_Message['city_url_name']
            url = URL_Message['URL']
            if re.sub('\s','',city) != '' and re.sub('\s','',city_url_name) != '' and re.sub('\s','',url) != '':
                print('继续上次记录，继续爬取的链接为：%s' % url)
                FangTianXia_Spider(city,city_url_name,url)
            else:
                # 删除csv文件
                if os.path.exists("fangtianxia.csv"):
                    os.remove("fangtianxia.csv")
                sys.exit('读取spider_url.json异常，无法继续上次记录，请删除json文件并重新运行!!!')
        except IndexError:
            # 删除csv文件
            if os.path.exists("fangtianxia.csv"):
                os.remove("fangtianxia.csv")
            sys.exit('读取spider_url.json文件出错，无法继续上次记录，请删除json文件并重新运行!!!')
    else:
        # 输入要爬取的城市名
        while True:
            city = input('输入要爬取的城市的中文名称：')
            if city != '':
                break

        # 获取城市名url前缀
        city_url_name = Fangtianxia_city(area_url, city)
        if city_url_name != None:
            url = base_url.format(city_url_name=city_url_name) + '/house/s/b91/'
            print('开始爬取的链接为：%s' % url)
            FangTianXia_Spider(city,city_url_name,url)
        else:
            sys.exit('获取不到对应的城市名URL前缀，请重新运行!!!')


if __name__ == '__main__':
    print ('爬取房天下新房信息')
    try:
        main()
    except KeyboardInterrupt:
        print('退出运行')
