#!/usr/bin/python2
#coding:utf-8


import MySQLdb
import MySQLdb.cursors
import sys
import os

DB_USER = 'xxx'
DB_PASS = 'xxx'
DB_HOST = 'xxx'
DB_NAME = 'xxx'
CONF_PATH = '/etc/sysconfig/network-script/'


def query(sql,num='1'):
    conn=MySQLdb.connect(
            host=DB_HOST,
            user=DB_USER,
            passwd=DB_PASS,
            db=DB_NAME,
            charset="utf8",
            cursorclass=MySQLdb.cursors.DictCursor
    )
    cursor = conn.cursor()
    cursor.execute(sql,num)
    rel = cursor.fetchone()
    cursor.close()
    return rel


def gen_conf(info, net_type, file_name='ifcfg-em0'):
    dev_name = file_name.split('-')[1]
    if net_type == 'lan':
        #将lanip的末位去掉并改成1
        gateway =  ('.').join(info['lanip'].split('.')[:3])+'.1'
        ip = info['lanip']
    elif net_type == 'wan':
        gateway = info['wanip']
        ip = info['wanip']

    net_conf = '''DEVICE="%s"
ONBOOT=yes
NETBOOT=yes
DEFROUTE=no
IPV6INIT=no
BOOTPROTO=static
IPADDR=%s
NETMASK=255.255.255.0
GATEWAY=%s
TYPE=Ethernet
NAME="%s"
''' %(dev_name, ip, gateway, dev_name)

    f = open(os.path.join(CONF_PATH, file_name), 'w')
    f.write(net_conf)
    f.close()

def conf_dev():
    fnames = os.listdir(CONF_PATH)
    dev_names = [ fname for fname in fnames if fname.startswith('ifcfg-' )]
    try:
        dev_names.index('ifcfg-lo')
    except ValueError:
        pass
    else:
        dev_lo = dev_names.index('ifcfg-lo')
        dev_names.remove(dev_lo)
    dev_names.sort()
    lan_file = dev_names[0]
    wan_file = dev_names[1]

    sql = 'select hostname,wanip,lanip,gateway from host where id=%s'
    info = query(sql,str(sys.argv[1]))
    if info['wanip'] != info['lanip']:
        gen_conf(info, 'lan', lan_file)
        gen_conf(info, 'wan', wan_file)
    else:
        gen_conf(info, 'lan', lan_file)

if __name__ == "__main__":
    conf_dev()
