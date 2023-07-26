# -*- coding: utf-8 -*-
# @Time    : 2023/7/26
# @Author  : 我的名字
# @File    : 看妹图批量爬取.py
# @Description : 用来搜索并下载写真图片，目标网址：https://kanmeitu1.cc

import os               # 创建目录
import requests         # 请求库
from lxml import etree  # 解析库
from time import sleep  # 程序休眠

# 全局变量
# 编号
num = 1
# 请求头
headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
        'cache-control': 'max-age=0',
        'Cookie': '__51vcke__K0L54LUTKRbipUWG=d45bc672-2238-5e69-8c6e-2d5dde1a1571; __51vuft__K0L54LUTKRbipUWG=1690256270465; __51vcke__K0KLKO0fwudqZoqt=fab87600-85e1-5dd5-90d9-0c56b528f9c9; __51vuft__K0KLKO0fwudqZoqt=1690256270471; __vtins__K0L54LUTKRbipUWG=%7B%22sid%22%3A%20%22848c3ec3-03b6-58f3-9d5d-b714df07c65d%22%2C%20%22vd%22%3A%201%2C%20%22stt%22%3A%200%2C%20%22dr%22%3A%200%2C%20%22expires%22%3A%201690277028000%2C%20%22ct%22%3A%201690275228000%7D; __51uvsct__K0L54LUTKRbipUWG=2; __vtins__K0KLKO0fwudqZoqt=%7B%22sid%22%3A%20%221c427f96-395d-575e-943f-e43b82473b88%22%2C%20%22vd%22%3A%201%2C%20%22stt%22%3A%200%2C%20%22dr%22%3A%200%2C%20%22expires%22%3A%201690277028007%2C%20%22ct%22%3A%201690275228007%7D; __51uvsct__K0KLKO0fwudqZoqt=2',
        'if-modified-since': '',
        'if-none-match': '',
        'sec-ch-ua': '"Not?A_Brand";v="8", "Chromium";v="108", "Microsoft Edge";v="108"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'none',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36 Edg/108.0.1462.76'
    }


def search():
    """
    :return:搜索结果的网址
    """
    key_world = str(input('请输入关键字:'))

    post_url = 'https://kanmeitu1.cc/e/search/' # 搜索引擎url
    data = {
        'keyboard': key_world,
        'tbname': 'news',
        'show': 'title',
        'tempid': '1'
    }  # 负载
    response = requests.post(url=post_url, data=data, headers=headers, allow_redirects=True) # 响应

    return response.url


def display(page_url):
    """
    :param page_url: 套图所在网址
    :return: 所有套图的网址列表
    """
    # 变量区
    nums = 1    # 套图序号
    total_pages = get_page(page_url) # 搜索结果总页数
    series_src_list = [] # 套图网址列表

    # 1.编列结果所有页面并解析
    for page in range(total_pages):
        data = {
            'page': page
        }
        tree = get_tree(base_url, data)
        # 套图链接列表,将每日套图链接存放上
        series_src_list += tree.xpath('//div[@id="list"]//li/a/@href')
        # 展示套图名称
        series_name_list = tree.xpath('//div[@id="list"]//li/a/@title')    # 套图名称列表,每页进来打印完即可替换掉不用保留
        for name in series_name_list:
            print(str(nums) + '、' + name)
            nums += 1
        # 请求过快会被封
        sleep(1)

    # 2.拼接套图完整网址
    for index in range(len(series_src_list)):
        series_src_list[index] = 'https://kanmeitu1.cc' + series_src_list[index]

    return series_src_list


# 得到解析树
def get_tree(url, data=None):
    """
    :param url:基础网址
    :param data: 网站需拼接的数据,可为空
    :return: tree，可直接进行xpath
    """

    if data is None:
        data = {}
    response = requests.get(url=url, params=data, headers=headers)
    response.encoding = 'utf-8'  # 记得编码！！！
    tree = etree.HTML(response.text)
    return tree

def get_page(page_url):
    """
    :param page_url:套图所在网址
    :return: 搜索结果总页数
    """
    # 找到套图总数量total
    data = {
        'page': 0
    }
    tree = get_tree(page_url, data)
    # 若只有一页将报错
    try:
        total = tree.xpath('//a[@title="总数"]/b/text()')[0]
    except:
        total = 25
    total = int(str(total))  # 不是字符串类型需要先强转为字符串再处理

    # 根据套图总数量判断总页数(一页最多25套)
    if total % 25 == 0:
        total_pages = int(total / 25)
    else:
        total_pages = int(total / 25) + 1

    return total_pages

# 下载图片
def down_load(series_src, path_name):
    """
    :param series_src:套图网址
    :param path_name:文件夹名称
    """
    global num
    # 1.解析图片原地址
    series_tree = get_tree(series_src)

    # img_total = series_tree.xpath('//p[@align="center"]//a')
    # img_total = int(str(img_total[0]).split('/')[1]) # 对原数据进行处理

    img_src_list = [] # 套图中每张图片的原址
    for img_num in range(1, 200):
        if img_num == 1:
            page_src = series_src
        else:
            page_src = series_src.replace('.html', '_' + str(img_num) + '.html')
        try:
            tree = get_tree(page_src)
            img_src_list.append(str(tree.xpath('//p[@align="center"]//img/@src')[0]))
        except:
            break
    print("图片共" + str(len(img_src_list)) + "张")
    # 2.解析套图名称
    title = str(series_tree.xpath('//div[@class="h"]//h1/text()')[0])
    print(title)

    # 3.修改名称
    title = title.replace('/', '')
    title = 'NO ' + str(num) + '、' + title  # 为文件夹编写序号
    num += 1  # 将编号加一
    print(title)

    # 4.创建套图文件夹
    path = 'G:/看妹图/' + path_name + '/' + title
    if not os.path.exists(path):
        os.makedirs(path)

    # 5.套图名称写入目录
    with open('G:/看妹图/' + path_name + '/目录.txt', 'a', encoding='utf-8') as fp:
        fp.write(title + '\n')
        fp.close()

    # 6.将套图中图片保存到文件夹中
    for img_index in range(0, len(img_src_list)):
        print('正在下载第'+str(img_index+1)+'个...')
        img_url = img_src_list[img_index]
        name = str(img_index+1) + '.jpg'
        img = None
        try:
            img = requests.get(url=img_url, headers=headers, timeout=5)
        except:
            try:
                img = requests.get(url=img_url, headers=headers, timeout=5)
            except:
                print("两次都失败！")
        # 写入
        if img is not None:
            with open(path + '/' + name, 'wb+') as f:
                f.write(img.content)
                f.close()
        print("下载完成！")


# 主程序
if __name__ == '__main__':
    while True:
        way = int(input('请选择模式 1-网址下载 2-搜索下载 3-关闭程序:'))
        if way == 1:
            src = input('请输入套图网址:')
            path_name = input('请输入存放的文件夹:')
            down_load(src,path_name)
        elif way == 2:
            while True:
                # 检索关键字
                base_url = search()
                img_src_list = display(base_url)
                #选择下载
                choice = int(input('请选择下载 1-全部下载 2-范围下载 3-编号下载 4-返回搜索 5-选择模式:'))
                if choice == 1:
                    print("准备下载全部套图...")
                elif choice == 2:
                    start_num = int(input('请输入套图起始编号：'))
                    end_num = int(input('请输入套图结尾编号：'))
                    img_src_list = img_src_list[start_num-1:end_num]
                    print("准备下载"+str(start_num)+'到'+str(end_num)+'套图...')
                elif choice == 3:
                    nums = int(input("请选择套图编号:"))
                    img_src_list = img_src_list[nums-1:nums]
                    print('准备下载'+str(nums)+'套图...')
                elif choice == 4:
                    continue
                elif choice == 5:
                    break
                else:
                    print("输入错误,请重新选择！")
                    continue
                # 获取存放地点及编号
                path_name = str(input("请输入存放的文件夹:"))
                num = int(input("请输入存放套图起始编号:"))
                # 下载
                for i in range(len(img_src_list)):
                    down_load(img_src_list[i], path_name)
                print('下载结束!')
                break
        elif way == 3:
            print('程序关闭！')
            exit(0)
        else:
            print('输入有误,请重新输入！')