#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import os

g = os.walk(r"./")

flist = []
content = '# BitTorrent协议中文翻译 \n \n'
for path, dir_list, file_list in g:
    for file_name in file_list:
        if file_name.endswith('.md'):
            flist.append(file_name)

flist.sort()
for file_name in flist:
    name = file_name[:-3].strip()
    content += '[%s](%s)\n' % (name, file_name)







f = open('./readme.md', 'w')
f.write(content)
f.close()
print (content)
