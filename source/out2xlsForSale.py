#!usr/bin/env python  
# -*- coding:utf-8 -*-
""" 
@author:51211 
@file: out2xlsForSale.py
@time: 2017/07/04 
"""
import requests
import xlsxwriter
from bs4 import BeautifulSoup
from source.sale_item import HouseItem

requests.adapters.DEFAULT_RETRIES = 5  # 增加重连次数
s = requests.session()
s.keep_alive = False  # 关闭多余连接


# s.proxies = {"https": "185.22.174.69:1448", "http": "180.118.128.38:9000", }


# 根据县区名字找到下面街道或者镇的url链接
def find_sub_link_by_region_name(param_url):
    global headers
    response = s.get(url=param_url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    region_items = soup.select('html body #container #content > div.div-border.items-list > div:nth-of-type(1)')
    children = region_items[0].contents
    region_items_details = children[1]
    selected_region = region_items_details.find("span", class_="selected-item")
    param_region_name = selected_region.string
    sub_items = region_items_details.find("div", class_="sub-items")
    sub_items_list = sub_items.find_all("a")
    # print(sub_items_list)
    param_sub_items_dict = {}
    for item in sub_items_list:
        # print(item.string)
        # print(item['href'])
        param_sub_items_dict[item.string] = item['href']
    return param_region_name, param_sub_items_dict


# 从当前页上把房产信息添加到house_items列表上
def add2house_items_from_one_page():
    global item_index
    global is_has_next
    soup = BeautifulSoup(sub_response.text, 'html.parser')
    house_list = soup.select('html body #container div #houselist-mod-new li')
    is_has_next = len(soup.find_all("a", class_="aNxt"))
    try:
        for item in house_list:
            item_index = item_index + 1
            print("**********************" + str(item_index) + "**************************")
            children = item.contents
            div_item_img = children[1]
            img_src = div_item_img.contents[1]['src']

            div_house_details = children[3]
            div_house_title = div_house_details.contents[1]

            house_list_title = div_house_title.contents[1]['title']
            div_details_item = div_house_details.contents[3]

            structure = div_details_item.contents[1].string
            area = div_details_item.contents[3].string
            floor = div_details_item.contents[5].string
            time = div_details_item.contents[7].string

            div_details_item2 = div_house_details.contents[5]
            address = div_details_item2.contents[1]['title']

            div_pro_price = children[5]
            price_det = div_pro_price.contents[1].contents[0].string + '万'
            unit_price = div_pro_price.contents[2].string

            # 构造item实例
            house_item = HouseItem(img_src, house_list_title, structure, area, floor, time, address, price_det,
                                   unit_price)
            house_item.my_print()
            house_items.append(house_item)
    except Exception as ex:
        print("except catch = %s" % str(ex))
        print(house_list)


# 根据城镇名在xls添加sheet
def add_sheet_by_town_name(param_key):
    ws = wb.add_worksheet(param_key)
    ws.set_column('A:A', 60)
    ws.set_column('D:D', 15)
    ws.set_column('E:E', 13)
    ws.set_column('F:F', 44)
    ws.set_column('H:H', 11)
    i = 0
    while i < len(house_items) + 1:
        if i == 0:
            ws.write(i, 0, '房产标题', )
            ws.write(i, 1, '几室几厅', )
            ws.write(i, 2, '面积', )
            ws.write(i, 3, '楼层', )
            ws.write(i, 4, '建成时间', )
            ws.write(i, 5, '地理位置', )
            ws.write(i, 6, '总价', )
            ws.write(i, 7, '均价', )
        else:
            ws.write(i, 0, house_items[i - 1].house_list_title, )
            ws.write(i, 1, house_items[i - 1].structure, )
            ws.write(i, 2, house_items[i - 1].area, )
            ws.write(i, 3, house_items[i - 1].floor, )
            ws.write(i, 4, house_items[i - 1].time, )
            ws.write(i, 5, house_items[i - 1].address, )
            ws.write(i, 6, house_items[i - 1].price_det, )
            ws.write(i, 7, house_items[i - 1].unit_price, )
        i = i + 1


# 根据县区名创建xls
def add_workbook_by_region_name(param_region_name):
    global wb, house_items, item_index, is_has_next, sub_response
    import os
    if not os.path.exists('../house_sale_xls'):
        os.makedirs('../house_sale_xls')
    wb = xlsxwriter.Workbook('../house_sale_xls/' + param_region_name + '.xlsx')
    for key in sub_items_dict.keys():
        print(key)
        sub_url = sub_items_dict[key] + 'p%s'
        print(sub_url)
        page_index = 1
        house_items = []
        item_index = 0
        is_has_next = 0
        while True:
            sub_response = s.get(url=sub_url % str(page_index), headers=headers)
            print('page_index=' + str(page_index))
            add2house_items_from_one_page()
            page_index = page_index + 1
            if is_has_next == 0:
                break

        print(len(house_items))

        add_sheet_by_town_name(key)
    wb.close()


if __name__ == '__main__':
    # sale_list index from 0 ~ 9
    sale_list = ['gongyeyuanqu',
                 'gaoxinqusuzhou',
                 'wuzhong',
                 'xiangcheng',
                 'wujiang',
                 'gushuqu',
                 'changshua',
                 'zhangjiagang',
                 'huqius',
                 'taicang']

    url = 'https://suzhou.anjuke.com/sale/%s/' % sale_list[6]

    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/' \
                 '59.0.3071.115 Safari/537.36'
    headers = {
        'User-Agent': user_agent,
    }
    region_name, sub_items_dict = find_sub_link_by_region_name(url)
    print(region_name)
    print(sub_items_dict.keys())

    add_workbook_by_region_name(region_name)
