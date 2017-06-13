#!/bin/bash

ip=""
remote_dir="/tmp"
passwd=""

expect <<EOF
   set timeout 200;
   spawn scp k $ip:$remote_dir/
   expect {
      "*yes/no*" {send "yes\r"; exp_continue}
      "*password*" {send "${passwd}\r"}
   }
expect eof;
EOF

expect <<EOD
   set timeout 200;
   spawn ssh $ip
   expect {
      "*yes/no*" {send "yes\r"; exp_continue}
      "*password*" {send "${passwd}\r"; exp_continue}
      "*#" {
         send "echo\r"
         send "whoami\r"
         send "date\r"
         send "exit\r"
      }
   }
expect eof;
EOD
