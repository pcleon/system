from bs4 import BeautifulSoup
import requests
import smtplib
import schedule
import time
import random
from email.mime.text import MIMEText
from email.header import Header

from_addr='wpctszz@qq.com'   #邮件发送账号
to_addrs='wpctszz@qq.com'   #接收邮件账号
qqCode=''   #授权码（这个要填自己获取到的）
smtp_server='smtp.qq.com'#固定写死
smtp_port=465#固定端口

last_title = ''

def mail(subject, msg):
    # 配置服务器
    stmp = smtplib.SMTP_SSL(smtp_server, smtp_port)
    stmp.login(from_addr, qqCode)

    # 组装发送内容
    message = MIMEText(msg, 'plain', 'utf-8')  # 发送的内容
    message['From'] = Header("电影巡查机器人", 'utf-8')  # 发件人
    message['To'] = Header("pc", 'utf-8')  # 收件人
    message['Subject'] = Header(subject, 'utf-8')  # 邮件标题

    try:
        stmp.sendmail(from_addr, to_addrs, message.as_string())
    except Exception as e:
        print('邮件发送失败--' + str(e), flush=True)
    print('邮件发送成功', flush=True)

def dy2018():
    print('run dy2018', time.asctime(time.localtime(time.time())), flush=True)
    global last_title
    baseurl = 'https://www.dy2018.com'
    url = baseurl + '/html/gndy/dyzz/index.html'
    html = requests.get(url)
    html.encoding = 'gb2312'
    html_doc = html.text
    soup = BeautifulSoup(html_doc, 'html.parser')
    titles = soup.find_all('a', class_='ulink')
    contents = soup.find_all('td', colspan="2", style="padding-left:3px")
    t0 = titles[0]
    t1 = titles[1]
    t0['href'] = baseurl + t0['href']
    t1['href'] = baseurl + t1['href']
    c0, c1 = contents[0].text, contents[1].text
    msg = f'''[{t0}]\r\n\r\n{c0}\r\nr\n[{t1}]\r\n\r\n{c1}'''
    if  last_title != t1:
        mail('电影上新', msg)
        last_title = t1



def dytt89_main():
    time.sleep(random.randint(1,60))
    global last_title
    print('run dytt89:', time.asctime(time.localtime(time.time())), flush=True)
    baseurl = 'https://www.dytt89.com'
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/53\
            7.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'
    }
    requests.packages.urllib3.disable_warnings()
    try:
        html = requests.get(baseurl, headers=headers, verify=False)
    except Exception as e:
        print(e)
        return
    html.encoding = 'gb2312'
    html_doc = html.text
    soup = BeautifulSoup(html_doc, 'html.parser')
    a = soup.select('#header > div > div.bd2 > div:nth-child(6) > div:nth-child(1) > div.co_content222 > ul > li > a' )
    del a[0]
    msg = ''
    if last_title != a[0].text:
        for i in a[:5]:
            i['href'] = baseurl + i['href']
            msg += str(i) + '\r\n'
        mail('电影上新', msg)
        last_title = a[0].text


if __name__ == '__main__':
    # dy2018()
    # schedule.every(10).minutes.do(dy2018)
    dytt89_main()
    schedule.every(10).minutes.do(dytt89_main)
    schedule.run_pending()
    while True:
        cur_hour = time.localtime().tm_hour
        print('check: ', time.asctime(time.localtime(time.time())), flush=True)
        if 9 <= cur_hour < 24:
            schedule.run_pending()
        time.sleep(30)
