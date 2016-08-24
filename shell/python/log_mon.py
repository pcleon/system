
#!/usr/bin/python
# -*- coding: UTF-8 -*-
'''
monitor nginx log when status error and alarm
'''
import time
import subprocess
import select
import sys


u = subprocess.Popen("grep IPADDR /etc/sysconfig/network-scripts/ifcfg-eth1 |cut -d\\' -f2",stdout=subprocess.PIPE,shell=True)
eth1=u.stdout.readline().split()[0]
filename = '/nginx/xxx.log'

f = subprocess.Popen(['tail','-F',filename],\
        stdout=subprocess.PIPE,stderr=subprocess.PIPE)
p = select.poll()
p.register(f.stdout)

while True:
    if p.poll(1) :
        line = f.stdout.readline()
        try:
          xx = int(line.split()[-5])
        except :
          print line
        if xx >= 400:
          cmd = '''xxx '%s'  '%s' ''' %(eth1, line)
          subprocess.call(cmd, shell=True)
