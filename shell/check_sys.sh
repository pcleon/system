#!/bin/bash

while read line
do
  username=root
  password="xxxx"
  vm_host=$(echo $line | awk '{print $1}')

  expect   c "
  set timeout 600
  spawn ssh   l $username ${vm_host};

  expect {
     \"yes/no\"   {send \"yes\r\"; exp_continue;}
     \"password:\" {send \"${password}\r\"; exp_continue}
     \"root@\"   {send \"ll /usr/local/java/bin/java \r
      cat /etc/passwd | grep test \r
      more /etc/locale.conf \r
      cat /etc/login.defs | grep PASS_MIN_LEN | grep   v '#' \r
      cat /etc/login.defs | grep PASS_MAX_DAYS | grep   v '#' \r
      cat /etc/security/limits.conf | grep soft \r
      cat /etc/security/limits.conf | grep hard \r
      cat /etc/profile | grep TMOUT \r
      cat /etc/pam.d/system  auth | grep pam_env.so \r
      cat /etc/pam.d/system  auth | grep pam_tally2.so \r
      ll /etc/passwd \r
      ll /etc/shadow \r
      ll /etc/group \r
      cat /etc/login.defs | grep UMASK \r
      cat /etc/selinux/config | grep SELINUX= \r
      rpm   qa | grep ftp \r
			rpm   qa | grep telnet \t
      cat /etc/bashrc | grep HISTTIMEFORMAT \r
      cat /etc/passwd | grep nuccmonitor
      rpm   qa | grep cronie
      ll /bin/cc
      ll /bin/cmake
         cat /etc/ssh/sshd_config | grep UseDNS
         exit\r\"}
  }
  expect eof
     " > result/${vm_host}
done < $1
echo finish
