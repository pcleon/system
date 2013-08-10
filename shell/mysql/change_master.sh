#!/bin/bash

if [ $# -ne 2 ];then
    echo -e "use\n\t $0 file 密码"
cat <<EOF
=====================================================================================
一定要在所有更改的库中确定已经执行stop slave (建议使用innotop)
并且从库已经同步主库的情况下执行,切记切记
file 文件中的格式为
原主库使用 m   ip port
新主库使用 new ip port
原从库使用 s   ip port
另一端主库 ms  ip port
=====================================================================================
EOF
	exit 2
fi

#定义你的密码
pass=$2
grep -v '^#' $1 > $1.new
FILE=$1.new

M_SELF_IP=$(cat $FILE|grep -w 'm'|awk '{print $2}')
M_SELF_PORT=$(cat $FILE|grep -w 'm'|awk '{print $NF}')

#停止主库并且等待所有从库同步到同一位置
mysql -uroot -p$pass -h $M_SELF_IP -P $M_SELF_PORT -e "stop slave;set global read_only=ON;"



#查找相应位置
M_MASTER_FILE=$(mysql -uroot -p$pass -h $M_SELF_IP -e "show master status\G"|grep -w 'File'|awk '{print $NF}')
M_MASTER_POS=$(mysql -uroot -p$pass -h $M_SELF_IP -e "show master status\G"|grep -w 'Position'|awk '{print $NF}')


MS_Host=$(mysql -uroot -p$pass -h $M_SELF_IP -P $M_SELF_PORT -e "show slave status\G"|grep -w 'Master_Host'|awk '{print $NF}')
MS_Port=$(mysql -uroot -p$pass -h $M_SELF_IP -P $M_SELF_PORT -e "show slave status\G"|grep -w 'Master_Port'|awk '{print $NF}')
MS_Master_Log_File=$(mysql -uroot -p$pass -h $M_SELF_IP -P $M_SELF_PORT -e "show slave status\G"|grep -w 'Master_Log_File'|awk '{print $NF}')
MS_Relay_Master_Log_File=$(mysql -uroot -p$pass -h $M_SELF_IP -P $M_SELF_PORT -e "show slave status\G"|grep -w 'Relay_Master_Log_File'|awk '{print $NF}')
MS_Exec_Master_Log_Pos=$(mysql -uroot -p$pass -h $M_SELF_IP -P $M_SELF_PORT -e "show slave status\G"|grep -w 'Exec_Master_Log_Pos'|awk '{print $NF}')

if [ $M_SLAVE_Master_Log_File != "$M_SLAVE_Relay_Master_Log_File" ];then
	echo "主库同步时日志Master_Log_File和Relay_Master_Log_File不同"
	exit 3
fi


#检查数据库同步情况
function check(){
	local S_IP=$1
	local S_PORT=$2
	local S_Master_Host=$(mysql -uroot -p$pass -h $S_IP -P $S_PORT -e "show slave status\G"|grep -w 'Master_Host'|awk '{print $NF}')
	local S_Master_Port=$(mysql -uroot -p$pass -h $S_IP -P $S_PORT -e "show slave status\G"|grep -w 'Master_Port'|awk '{print $NF}')
	local S_Master_Log_File=$(mysql -uroot -p$pass -h $S_IP -P $S_PORT -e "show slave status\G"|grep -w 'Master_Log_File'|awk '{print $NF}')
	local S_Relay_Master_Log_File=$(mysql -uroot -p$pass -h $S_IP -P $S_PORT -e "show slave status\G"|grep -w 'Relay_Master_Log_File'|awk '{print $NF}')
	local S_Exec_Master_Log_Pos=$(mysql -uroot -p$pass -h $S_IP -P $S_PORT -e "show slave status\G"|grep -w 'Exec_Master_Log_Pos'|awk '{print $NF}')
	local S_Seconds_Behind_Master=$(mysql -uroot -p$pass -h $S_IP -P $S_PORT -e "show slave status\G"|grep -w 'Seconds_Behind_Master'|awk '{print $NF}')
	#if [ $M_SELF_IP != $S_Master_Host ] || [ $M_SELF_PORT != $S_Master_Port ] || [ "$M_MASTER_FILE" != "$S_Relay_Master_Log_File" ] || [ "$M_MASTER_POS" != "$S_Exec_Master_Log_Pos" ] || [ $S_Seconds_Behind_Master != "NULL" ];then
	if [ $M_SELF_IP != $S_Master_Host ] || [ $M_SELF_PORT != $S_Master_Port ] || [ "$M_MASTER_FILE" != "$S_Relay_Master_Log_File" ] || [ "$M_MASTER_POS" != "$S_Exec_Master_Log_Pos" ] || [ $S_Seconds_Behind_Master != "NULL" ];then
	echo -e "\
=========
\e[31;49;1m $S_IP $S_PORT  位置或者状态错误 !!!!!!!!!!
老主库位置 $M_SELF_IP $M_SELF_PORT $M_MASTER_FILE $M_MASTER_POS  
老同步位置 $S_Master_Host $S_Master_Port $S_Relay_Master_Log_File $S_Exec_Master_Log_Pos
老同步状态 $S_Seconds_Behind_Master\e[31;49;0m
"
	else
		echo "$S_IP $S_PORT 已同步"
	fi
}

cat <<EOF
*****************************
老主库的信息
$M_SELF_IP $M_SELF_PORT $M_MASTER_FILE $M_MASTER_POS
EOF

cat<<EOF
==========================================================
检查是否已经同步完全
EOF

grep -w 's\|ms\|new' $FILE | 
while read xx s_ip s_port;do
	check $s_ip $s_port
done



NEW_M_IP=$(cat $FILE|grep 'new'|awk '{print $2}')
NEW_M_PORT=$(cat $FILE|grep 'new'|awk '{print $NF}')

#查找相应位置
NEW_M_FILE=$(mysql -uroot -p$pass -h $NEW_M_IP -e "show master status\G"|grep -w 'File'|awk '{print $NF}')
NEW_M_POS=$(mysql -uroot -p$pass -h $NEW_M_IP -e "show master status\G"|grep -w 'Position'|awk '{print $NF}')
cat <<EOF
=========================
确定新主库和老主库的show master status信息是否正确
信息 IP :: 端口 :: 文件 :: 位置
老 $M_SELF_IP $M_SELF_PORT $M_MASTER_FILE $M_MASTER_POS 
新 $NEW_M_IP $NEW_M_PORT $NEW_M_FILE $NEW_M_POS 
=========================
EOF

read -p "确定更改?(y/n):" answer
case $answer in 
Y|y)
	continue;;
N|n|*)
	echo "已经取消,将取消原主库的读锁,请手动start slave;"
	mysql -uroot -p$pass -h $M_SELF_IP -P $M_SELF_PORT -e "set global read_only=OFF;"
	#恢复函数
	exit 0
esac



#将所有原来的从库和老主库指向新的主库
function change_slave_to_new_master(){
grep -w 's\|ms\|m' $FILE |
while read xx SLAVE_IP SLAVE_PORT;do
echo -e "===========newslave=========NEW $SLAVE_IP $SLAVE_PORT status========================="
    mysql -uroot -p$pass -h$SLAVE_IP -P $SLAVE_PORT -e "CHANGE MASTER TO MASTER_HOST='$NEW_M_IP',  MASTER_USER='root', MASTER_PASSWORD='$pass', MASTER_PORT=$NEW_M_PORT, MASTER_LOG_FILE='$NEW_M_FILE', MASTER_LOG_POS=$NEW_M_POS;"
	mysql -uroot -p$pass -h$SLAVE_IP -P $SLAVE_PORT -e " show slave status\G"|grep -w 'Master_Host\|Master_Port\|Master_Log_File\|Relay_Master_Log_File\|Exec_Master_Log_Pos'
done
}

#将新主库作为另外一边主库的从库
function change_new_master_to_ms(){
grep -w 'new' $FILE|
while read xx NEW_MASTER_IP NEW_MASTER_PORT;do
echo -e "====新主库====$NEW_MASTER_IP $NEW_MASTER_PORT =同步状态====="
    mysql -uroot -p$pass -h$NEW_MASTER_IP -P $NEW_MASTER_PORT -e "CHANGE MASTER TO MASTER_HOST='$MS_Host',  MASTER_USER='root', MASTER_PASSWORD='$pass', MASTER_PORT=$MS_Port, MASTER_LOG_FILE='$MS_Relay_Master_Log_File', MASTER_LOG_POS=$MS_Exec_Master_Log_Pos;"
    mysql -uroot -p$pass -h$NEW_MASTER_IP -P $NEW_MASTER_PORT -e " show slave status\G"|grep -w 'Master_Host\|Master_Port\|Master_Log_File\|Relay_Master_Log_File\|Exec_Master_Log_Pos'
done
} 


change_new_master_to_ms
change_slave_to_new_master


#恢复原主库的读锁
mysql -uroot -p$pass -h $M_SELF_IP -P $M_SELF_PORT -e "set global read_only=OFF;"

echo "已经更改完成,请确认后手动对从库执行start slave(建议使用innotop)"
