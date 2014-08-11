#!/usr/bin/python
#coding:utf-8

import urllib2
import re
import sys
from bs4 import BeautifulSoup
from optparse import OptionParser

#查找要答题的网页的所有题目
def findQestion(req_url):
    soup = BeautifulSoup(req_url)
    req = []
    s1 = soup.find_all('tr',height='25')
    for line in s1:
        reg = u"\d分"
        if re.search(reg,line.get_text()):
            req += [line.td.get_text().split('\n')[0]]
    return req

#利用问题去匹配已有答案的页面,找出答案-_-
def getAnser(question , webcontent ):
    soup = BeautifulSoup(webcontent)
    s1 = soup.find_all('tr',height='25')
    ans = []

    for line in s1:
        if re.search(question, line.get_text()):
            for choice in line.td.find_all('img', src = re.compile(u's.gif$')):
               if re.search(u'ed_s.gif',str(choice)):
                   ans += [1]
               else:
                   ans += [0]
            return ans
            break



def main():
    usage = "usage: %prog -a args -q args"
    parser = OptionParser(usage)
    parser.add_option('-q', '--question',
                        action='store', dest='question', type='string',
                        help='the question web page ')
    parser.add_option('-a', '--answer',
                        action='store', dest='answer', type='string',
                        help='the answered web page ')
    options, args = parser.parse_args()

    try:
        ans_url = options.answer
        ask_url = options.question

        ans_html=urllib2.urlopen(ans_url).read()
        ans_content = ans_html.decode('gb2312')

        ask_html=urllib2.urlopen(ask_url).read()
        ask_content = ask_html.decode('gb2312')

        asks = findQestion(ask_content)
        for ask in asks:
            print ask
            print getAnser(ask[5:],ans_content)
    except:
        parser.print_help()



if __name__ == "__main__":
    main()
