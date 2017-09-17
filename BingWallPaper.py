import os
from html.parser import HTMLParser
import requests
import threading
import re


class BingHTMLParser(HTMLParser):

    page_count = 1

    def __init__(self, *, convert_charrefs=True):
        super().__init__(convert_charrefs=convert_charrefs)
        self.src_list = list()
        self.max_page = 1

    def set_max_page(self, val):
        self.max_page = val

    def error(self, message):
        print("[ERROR] - %s" % message)

    def handle_starttag(self, tag, attrs):
        if tag == "img":
            for attr in attrs:
                if attr[0] == "src":
                    self.src_list.append(self.convert_big_image(attr[1]))

    def convert_big_image(self, img_src):
        # convert 'http://images.ioliu.cn/bing/FoehrAerial_EN-AU11365731144_320x240.jpg'
        # to 'http://images.ioliu.cn/bing/FoehrAerial_EN-AU11365731144_1920x1080.jpg'
        return img_src.replace("320x240", "1920x1080")


def download_img(p):
    """
    :param p: HTML parser
    :return: None
    """
    while len(p.src_list) != 0:
        url = p.src_list.pop()
        file_name = url[url.rfind("/") + 1:]

        if os.path.exists(file_name):
            return
        else:
            response = requests.get(url)
            if response.status_code == 200:
                with open(file_name, "wb") as img_file:
                    img_file.write(response.content)
                print("Save image as %s" % file_name)
            else:
                print("Error with response status %s" % response.status_code)


def request_page(p, _lock):
    """
    request Bing HTML by page count
    :param p: HTML parser
    :param _lock: threading lock
    :return: 
    """
    while p.page_count <= p.max_page:
        _lock.acquire()
        try:
            page = p.page_count
            p.page_count += 1
        finally:
            _lock.release()
        print("Start request HTML page %s" % page)
        resp = requests.get("https://bing.ioliu.cn/?p=" + str(page))
        if resp.status_code == 200:
            html_str = resp.content.decode("utf8")
            print("Start parse page %s HTML..." % page)
            p.feed(html_str)
        else:
            print("[ERROR] - Request error with code %s" % resp.status_code)


def mkdir():
    if not os.path.exists("bing"):
        os.makedirs("bing")
    os.chdir("bing")


def get_max_page_num():
    resp = requests.get("https://bing.ioliu.cn/?p=1")
    if resp.status_code == 200:
        html_str = resp.content.decode("utf8")
        pattern = re.compile('<span>1 / \\d+</span><a href="/\?p=', re.S)
        max_page = 1
        try:
            match_str = re.findall(pattern, html_str)[0]
            pattern = re.compile('\\d+', re.S)
            max_page = re.findall(pattern, match_str)[1]
        except Exception:
            print("Error in find max page num")
        finally:
            return int(max_page)
    else:
        print("[ERROR] - Request error with code %s" % resp.status_code)
        return 1


def main():
    lock = threading.Lock()
    print("Enter directory bing...")
    mkdir()

    print("Create HTML Parser...")
    parser = BingHTMLParser()

    print("Get Max Page Number...")
    parser.set_max_page(get_max_page_num())

    # request all page and put image url in list
    threads = list()
    for i in range(0, 8):
        threads.append(threading.Thread(target=request_page, args=(parser, lock,)))

    for thread in threads:
        thread.start()
    while parser.page_count < parser.max_page:
        pass

    # foreach url in url_list and download image
    threads = list()
    for i in range(0, 8):
        threads.append(threading.Thread(target=download_img, args=(parser,)))

    for thread in threads:
        thread.start()

if __name__ == '__main__':
    main()
