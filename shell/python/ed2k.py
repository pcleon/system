#!/usr/bin/python
#encoding: utf-8
'''
抓yyets的电驴链接
'''

import re,urllib2,sys
def ed2k(url=''):
    f=urllib2.urlopen(url)
    t=f.read()
    reg=r'(?<=ref=")ed2k:.*?\|/?(?=")'
    link = re.findall(reg,t)

    for i in sorted(set(link)):
        if "mkv" in i:
            print i

if __name__ == "__main__":
    try:
        url = str(sys.argv[1])
        ed2k(url)
    except IndexError:
        print "use: " + sys.argv[0] + " url"
