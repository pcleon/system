#!/usr/bin/env python
#coding=utf-8
'''
这是模仿在各种查询IP解析的网站上输入IP查询地址的过程
'''
#usage: python filename 8.8.8.8

import urllib, re, sys
import json
import threading

class bcolors:
    HEADER = '\033[95m'
    OK_BLUE = '\033[94m'
    OK_GREEN = '\033[92m'
    WARING_YELLOW = '\033[93m'
    FAIL = '\033[36m'
    FLASHING = '\033[35m'
    CRITICAL_RED = '\033[31m'
    END = '\033[0m'

def getip_qq(ip='8.8.8.8'):
        '''
        use QQ database
        '''
        #请求URL，以及请求解析的URL格式变化
        url = "http://ip.qq.com/cgi-bin/searchip"
        data = "searchip1=" + ip

        #不同的网站网页字符编码不同，匹配不同的内容，封装不同的编码
        html = urllib.urlopen(url, data).read().decode("gb2312")

        #查询匹配的内容
        pat = re.compile(r'<span>(.*)</span></p>')
        result = re.findall(pat, html)
        print "ip.qq.com 查询地址："
        print '    ' + bcolors.OK_GREEN + ip + bcolors.END + " < --- > " + bcolors.WARING_YELLOW + result[0].encode("utf-8").replace('&nbsp;', '') + bcolors.END

def getip_ip138(ip='8.8.8.8'):
        '''
        use ip138
        '''
        url = "http://ip138.com/ips1388.asp?ip=%s&action=2" % ip
        html = urllib.urlopen(url).read().decode("gb2312")

        #这是要查询匹配的内容
        string = "本站主数据：".decode("utf-8")
        # print string
        result = re.findall(string+'([^<>]+)</li>',html)
        print "ip138.com 查询地址："
        print '    ' + bcolors.OK_GREEN + ip + bcolors.END + " < --- > " + bcolors.WARING_YELLOW + result[0].encode("utf-8").replace(' ', '') + bcolors.END

def getip_cn(ip='8.8.8.8'):
        '''
        use ip.cn
        '''
        url = "http://ip.cn/index.php?ip=%s" % ip
        html = urllib.urlopen(url).read().decode("utf-8")
        string = "来自：".decode("utf-8")
        result = re.findall(string+'([^<>]+)</p>',html)
        print "ip.cn 查询地址："
        print '    ' + bcolors.OK_GREEN + ip + bcolors.END + " < --- > " + bcolors.WARING_YELLOW + result[0].encode("utf-8").replace(' ', '') + bcolors.END

def getip_tb(ip='8.8.8.8'):
        '''
        use taobao.com
        '''
        url = "http://ip.taobao.com/service/getIpInfo.php?ip=%s" % ip
#        html = urllib.urlopen(url).read().decode("utf-8")
        html = urllib.urlopen(url).read()
        string = "来自：".decode("utf-8")
        result = json.loads(html)
        print "ip.taobao.com 查询地址："
        location = "%s%s%s" %(result['data']['country'],result['data']['region'],result['data']['isp'])
        print '    ' + bcolors.OK_GREEN + ip + bcolors.END + " < --- > " + bcolors.WARING_YELLOW + location + bcolors.END



if __name__ == '__main__':
    try:
        threading.Thread(target=getip_qq, args=(sys.argv[1],)).start()
        threading.Thread(target=getip_ip138, args=(sys.argv[1],)).start()
        threading.Thread(target=getip_cn, args=(sys.argv[1],)).start()
        threading.Thread(target=getip_tb, args=(sys.argv[1],)).start()
    except IndexError:
        print "Usage: %s ip地址" %(sys.argv[0])
        sys.exit() # exit the program
