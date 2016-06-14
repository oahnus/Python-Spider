# -*- coding: utf-8 -*-
import re


class Tool:
    # 去掉img标签
    removeImg = re.compile('<img.*?>| {1,7}|&nbsp;')
    # 删除超链接标签
    removeAddr = re.compile('<a.*?>|</a>')
    # 替换换行标签为\n
    replaceLine = re.compile('<tr>|<div>|</div>|</p>')
    # 将表格<td>替换为\t
    replaceTD = re.compile('<td>')
    # 替换换行符
    replaceBR = re.compile('<br><br>|<br>')
    # 将其余标签替换
    removeExtraTag = re.compile('<.*?>')
    # 删除多余空行
    removeNoneLine = re.compile('\n+')

    def replace(self, x):
        x = re.sub(self.removeImg, '', x)
        x = re.sub(self.removeAddr, '', x)
        x = re.sub(self.replaceLine, '\n', x)
        x = re.sub(self.replaceTD, '\t', x)
        x = re.sub(self.replaceBR, '\n', x)
        x = re.sub(self.removeExtraTag, '', x)
        x = re.sub(self.removeNoneLine, '\n', x)
        # strip() 将前后多余的内容删除
        return x.strip()
