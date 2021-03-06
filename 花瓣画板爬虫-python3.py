# -*- coding: utf-8 -*-

import urllib.request
import re
import os


class Spider:
    # 初始化函数
    def __init__(self):
        self.siteURL = ''
        self.originURL = ''

    # 获取花瓣网画板页面代码
    def get_board_page(self):
        # url = self.siteURL
        try:
            request = urllib.request.Request(self.siteURL)
            response = urllib.request.urlopen(request)
        except urllib.request.HTTPError as e:
            if e.code == 404:
                print("Board Not Found")
                return ''
        return response.read().decode('utf-8')

    # 获取画板内所包含的图片的ID
    def get_img_id(self, board_page):
        pattern_img = re.compile('<div data-id="\d*"', re.S)
        ids = re.findall(pattern_img, board_page)
        return ids

    # 获取画板名称，用于创建相对应的文件夹
    def get_board_name(self, page):
        pattern = re.compile('<h1 class="board-name">.*?</h1>', re.S)
        name = re.search(pattern, page).group()
        # 将含有画板名的h1标签中的文本提取出，获取name字符串的子串
        name = name[23:-5]
        return name

    # 获取包含图片资源的页面代码，此页面为原始尺寸的图片页面
    def get_img_page(self, index):
        try:
            url = 'http://huaban.com/pins/' + str(index) + '/zoom/'
            request = urllib.request.Request(url)
            response = urllib.request.urlopen(request)
        except urllib.request.HTTPError as e:
            if e.code == 404:
                print("Image Not Found")

            return ''
        return response.read().decode('utf-8')

    # 获取图片url地址
    def get_img(self, page):
        pattern = re.compile('<div id="zoomr_body".*?>(.*?)<!--', re.S)
        content = re.search(pattern, page)
        pattern_img = re.compile('<img.*?src="(.*?)"', re.S)
        # image = re.findall(patternImg, content)
        if content:
            image = re.search(pattern_img, content.group(1))
            if image:
                return 'http:' + image.group(1)
            else:
                return ''

    # 保存图片，传入参数为图片的url地址，要保存在本地的文件名称
    def save_img(self, image_url, file_name):
        u = urllib.request.urlopen(image_url)
        data = u.read()
        f = open(file_name, 'wb')
        f.write(data)
        print(u"Save Image As ", file_name)
        f.close()

    # 创建目录，目录名为画板的名称
    def mkdir(self, name):

        is_exist = os.path.exists(name)
        if not is_exist:
            # 如果不存在则创建目录
            os.makedirs(name)
        os.chdir(name)

    # 保存画板内的所有图片
    def save_board(self, url):

        url = url.strip()
        # 设置画板的url
        self.siteURL = url
        # 获取画板的html
        board = self.get_board_page()

        # 获取画板的名称
        name = self.get_board_name(board)

        # 新建目录
        self.mkdir(name)

        while(1):
            # 设置画板的url
            self.siteURL = url
            # 获取画板的html
            board = self.get_board_page()
            # 提取画板页面中的图片id
            ids = self.get_img_id(board)

            # 如果列表为空 返回
            if len(ids) == 0:
                return

            # 存储图片
            for index in ids:
                try:
                    # ids中的id存在其他字符，获取子串来提取出index
                    index = index[14:-1]
                    print(index)
                    # 获取图片的资源页面
                    imgpage = self.get_img_page(index)
                    # 提取图片的url地址
                    img = self.get_img(imgpage)
                    if not img == '':
                        # 保存图片
                        self.save_img(img, index + '.jpg')
                        # print img
                except Exception:
                    # 如果中间出现错误，跳过此图片，继续从下个图片地址下载存储图片
                    continue
            # 最后一个图片的ID
            lastImg = ids[-1][14:-1]
            # 花瓣网的画板内有下拉加载，下拉加载的请求url为下面url格式，
            # 通过将刷新前的最后一张图片id加入请求中，就可获取新的图片列表
            url = self.originURL + '?irr486cj&max=' + str(lastImg) + '&limit=20&wfl=1'
            # curl "http://huaban.com/boards/30445176/?irr486cj&max=805536368&limit=20&wfl=1"
            print(url)


# 创建爬虫实例
spider = Spider()
# 获取输入的画板url
url = input("board url:")
spider.originURL = url

# 执行保存画板方法
spider.save_board(url)
# 结束
print('Complete!!!')
input("Enter To Exit")

