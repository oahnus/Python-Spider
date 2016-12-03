# -*- coding: utf-8 -*-

import urllib.request
import re
import os
import time
import http.cookiejar

class Spider:
    def __init__(self):
        self.website = 'http://www.jj20.com'
        self.base_url = 'http://www.jj20.com/bz/ktmh/dmrw/'
        self.headers = {
            'Accept' : 'image/webp , image/* , */*;q = 0.8',
            'Accept-Encoding':'gzip , deflate , sdch',
            'Accept-Language':'zh-CN zh;q = 0.8',
            'Cache-Control':'max-age = 0',
            'Connection':'keep-alive',
            'Host':'pic.jj20.com',
            'If-None-Match':'"92849986c11cd1:4eb"',
            'Referer':'http://www.jj20.com/bz/ktmh/dmrw/',
            'User-Agent':'Mozilla / 5.0(Windows NT 10.0;WOW64) AppleWebKit / 537.36(KHTML, like Gecko) Chrome / 54.0.2840.99 Safari / 537.36'
        }

        cookie_file = 'cookie.txt'
        cookie = http.cookiejar.MozillaCookieJar(cookie_file)
        handler = urllib.request.HTTPCookieProcessor(cookie)
        self.opener = urllib.request.build_opener(handler)
        self.opener.open('http://www.jj20.com/bz/ktmh/dmrw/9333.html#q')
        cookie.save(ignore_discard=True, ignore_expires=True)

    # 获取页面html代码
    def get_website_page_html(self, site_url):
        try:
            request = urllib.request.Request(site_url)
            response = self.opener.open(request)
        except urllib.request.HTTPError as e:
            if e.code == '404':
                print('Page Not Found')
                return ''
        return response.read().decode('gbk')

    # 获取分类下所有分页的页面url
    def get_all_page_url(self, page_html):
        pattern_album_option_label = re.compile('<option value=\'(.*?)\'', re.S)
        page_urls = re.findall(pattern_album_option_label, page_html)
        return page_urls

    # 获取所有画集的url
    def get_all_albums_url_from_page(self, page_html):
        pattern_album_url = re.compile('<img src="(.*?)"', re.S)
        album_urls = re.findall(pattern_album_url, page_html)
        return album_urls

    # 获取每个画集中图片的数量
    def get_image_number_from_page(self, page_html):
        pattern_image_number_ = re.compile('</a>\((\d*)张', re.S)
        image_number = re.findall(pattern_image_number_, page_html)
        return image_number

    # 获取画集名称
    def get_album_name(self, page_html):
        pattern_album_name = re.compile('</a>\r\n<a href=".*?>(.*?)</a>', re.S)
        album_name = re.findall(pattern_album_name, page_html)
        return album_name

    # 保存图片到本地
    def save_image(self, image_url, file_name):
        print(u"Save Image As ", file_name)
        # 此处获取图片保存没有处理好，总是会下不到图片，不知道是不是Referer活着cookie的问题
        # 只能不断尝试去获取，偶尔会有成功的情况
        # TODO 改变获取图片的方式？
        while(1):
            request = urllib.request.Request(image_url, headers=self.headers)
            u = self.opener.open(request)
            data = u.read()
            f = open(file_name, 'wb')
            f.write(data)

            f.close()
            if os.path.getsize(file_name) > 16384:
                break

    # 创建目录，目录名为画板的名称
    def mkdir(self, dir_name):
        # 替换标题中的非法字符
        dir_name = dir_name.replace('<b>', '')
        dir_name = dir_name.replace('</b>', '')
        dir_name = dir_name.replace('/', '')
        dir_name = dir_name.replace('\\', '')

        is_exist = os.path.exists(dir_name)
        if not is_exist:
            # 如果不存在则创建目录
            os.makedirs(dir_name)
        os.chdir(dir_name)

    def run_spider(self):

        # 获取初始页面html代码
        init_page_html = self.get_website_page_html(self.base_url)
        # 从html中获取动漫人物分类下的所有页面的url
        page_urls = self.get_all_page_url(init_page_html)

        # 创建根目录
        self.mkdir("jj20.com")

        # 遍历所有页面
        for page_url in page_urls:
            page_html = self.get_website_page_html(spider.base_url+page_url)
            # print(page_html)
            pattern_album_url = re.compile('<li>\r\n<a href="(.*?)"', re.S)
            urls = re.findall(pattern_album_url, page_html)
            # print(urls)
            # return
            album_urls = spider.get_all_albums_url_from_page(page_html)
            # 获取画集中图片个数和名字
            album_image_numbers = self.get_image_number_from_page(page_html)
            album_names = self.get_album_name(page_html)

            print("page "+str(page_urls.index(page_url)+1))
            # 遍历页面中所有的画集
            for album_url in album_urls:
                index = album_urls.index(album_url)
                self.headers['Referer'] = self.website+urls[index]
                print(self.headers['Referer'])
                # print(album_url)
                # 获取画集数量
                # print(album_image_numbers[index])
                pic_url = album_url[:7] + 'pic' + album_url[10:-7] + '.jpg'
                # print(pic_url)
                n = pic_url[pic_url.index('-')+1:-4]

                # 创建画集名称的文件目录
                name = album_names[index]
                self.mkdir(name)

                print(name)
                # 打印当前目录
                # print(os.getcwd())
                # 从画集中下载图片
                for i in range(0, int(album_image_numbers[index])):
                    try:
                        pic_url = pic_url[0:pic_url.index('-')+1]+str(int(n)+i)+'.jpg'
                        # print(pic_url)
                        # 保存图片到本地
                        self.save_image(pic_url, pic_url[pic_url.index('-')+1:])

                    except Exception:
                        continue
                os.chdir('../')
        print('complete!!!')

spider = Spider()

# 输入网站某个分类的url
# http://www.jj20.com/bz/zrfg/

# url = input('输入分类主页的url')
# spider.base_url = url

# 默认下载动漫人物分类下的图片

# 执行
spider.run_spider()
