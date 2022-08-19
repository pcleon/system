#!/usr/bin/env python3
import os
import pathlib
import sqlite3
import subprocess
import xml.etree.ElementTree as ET

import requests
from loguru import logger
from validators import ipv4

url = "x.x.x/myip"
db_file = "myip.db"
# firewall_file = "public.xml"
firewall_file = "/etc/firewalld/zones/public.xml"
current_ip = requests.get(url)
headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36"
}

path = pathlib.Path(__file__)
logfile = path.parent.joinpath('fw.log')
os.chdir(path.parent)
formatter = "{time}|{level}|{message}"
logger.remove(handler_id=None)  # 清除之前的设置
logger.add(logfile, format=formatter, rotation="50 MB")  # Automatically rotate too big file


def parser_xml(fname):
    tree = ET.ElementTree(file=fname)
    # 通过firewalld配置文件中/32的ip生成ip列表
    xml_ips = [
        x.attrib["address"].split("/")[0]
        for x in tree.findall('.//rule[@family="ipv4"]/source[@address]')
        if "/32" in x.attrib["address"]
    ]
    return xml_ips


def refresh_firewall(web_ips):
    db_ips = []
    xml_ips = parser_xml(firewall_file)
    # 求差集检查ip是不是不在xml中
    web_diff_ip = set(web_ips) - set(xml_ips)
    if web_diff_ip:
        # 获取db中的ips
        logger.info(f"有新ip: {web_ips}")
        with sqlite3.connect(db_file) as conn:
            cur = conn.cursor()
            query = cur.execute("""SELECT DISTINCT ip FROM main.myip ORDER BY id DESC """)
            db_ips = [row[0] for row in query]
        # db和xml的ip做交集,将交集的IP删除
        intersection = set(xml_ips) & set(db_ips)
        # 删除ip
        for delete_ip in intersection:
            remove_cmd = f"""/bin/firewall-cmd --permanent --remove-rich-rule="rule family='ipv4' source address='{delete_ip}/32' accept" """
            run_shell(remove_cmd)
        #  添加web中的ip
        for add_ip in web_diff_ip:
            add_cmd = f"""/bin/firewall-cmd --permanent --add-rich-rule="rule family='ipv4' source address='{add_ip}/32' accept" """
            res = run_shell(add_cmd)
            if not res[0]:
                # 写入db
                with sqlite3.connect(db_file) as conn:
                    cur = conn.cursor()
                    cur.execute(
                        f"""INSERT INTO main.myip (ip, ts) VALUES ('{add_ip}', datetime(strftime('%s','now'), 'unixepoch', 'localtime'))"""
                    )
                logger.info(f"添加{add_ip}成功")
            else:
                logger.error(f"添加{add_ip}失败")
        run_shell("/bin/firewall-cmd --reload")
    # 有交集且和当前ip一样时,不操作
    else:
        logger.info("ip没变化,不操作")


def run_shell(cmd):
    res = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    stdout, stderr = res.communicate()
    return res.returncode, stdout, stderr, res.pid


def job():
    req = requests.get(url, headers=headers, timeout=10)
    if req.status_code < 400:
        web_ips = [ip for ip in req.text.split() if ipv4(ip)]
        refresh_firewall(web_ips)
    else:
        logger.error("获取ip列表失败")


if __name__ == "__main__":
    job()
