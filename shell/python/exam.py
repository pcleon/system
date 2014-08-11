#!/usr/bin/python
#coding:utf-8
BASE_URL = '' #考试的基地址
import urllib2
import re
import sys
from bs4 import BeautifulSoup
reload(sys)
sys.setdefaultencoding('utf-8')

def getAnser(question , webcontent ):
    soup = BeautifulSoup(webcontent)
    s1 = soup.find_all('tr',height='25')
    ans = []

    for line in s1:
        if re.search(question.encode('utf-8'), str(line)):
            matchline = line
            for choice in matchline.td.find_all('img', src = re.compile(u's.gif$')):
               if re.search('ed_s.gif',str(choice)):
                   ans += [1]
               else:
                   ans += [0]
            return ans
            break

def findQestion(req_url):
    soup = BeautifulSoup(req_url)
    req = []
    s1 = soup.find_all('tr',height='25')
    for line in s1:
        if re.search('\d分',str(line)):
            req += [line.td.get_text().split()[0]]
    return req


def main():
    uri = sys.argv[1]
    html=urllib2.urlopen(BASE_URL + uri)
    s=html.read()
    content = s.decode('gb2312').encode('utf-8')
    qes = findQestion(content)
    for qnum in qes:
        print qnum
        print getAnser(qnum,content)



if __name__ == "__main__":
    main()
