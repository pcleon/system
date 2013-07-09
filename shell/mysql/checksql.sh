#!/bin/bash
phone="88888"
name="pcleon"
PASS=your_password

function show(){
    echo "HOST=$1 IP=$2 PORT=$3"
    num=$(echo "show slave status\G"|mysql -uroot -p$PASS -h$2 -P $3|grep Last_Errno|awk '{print $NF}')
    echo -e "status====$num \n$(date +%Y%m%d-%H:%M)"

if [ x"$num" = x1062 -o x"$num" = x1690 ];then
    echo "error!!!!"
    time=$(date +%H:%M)
    for mm in $name
    do
        echo "show slave status\G"|mysql -uroot -p$PASS -h$2 -P$3|mail -s "Database $1 $2 $3 error_SQL!!!!!" $mm@domain.com
    done
    content="$1:$2:+err_num=$num+port=$3+and+skip+$time"
#####
#here do something notice adm know
####
fi
if [ x"$num" = x1062 -o x"$num" = x1690 ];then
    echo " slave stop;set global sql_slave_skip_counter=1;slave start;"|mysql -uroot -p$PASS -h$2 -P$3
    echo "skip 1"
fi

}

cat bj_list|grep -v "^#\|^$"|
 while read HOST IP PORT
do
        show $HOST $IP $PORT
        echo =========================
done
