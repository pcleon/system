#!/bin/bash

if [ $# -ne 1 ];then
    echo -e "Use:\n\t $0 mysql_path"
    exit 3
fi

report_user=''
PASSWD=
MYSQL_USER=root
thread=4
MEM=2
LOG_PATH=/var/log/backup_mysql/inc
LOG_TIME=$(date +%Y%m%d%H%M%S)
MYSQL_PATH=$1
DB_NAME=$(basename $MYSQL_PATH)
BACKUP_PATH=/data/backup/$DB_NAME
BASE_DIR=$(cat $BACKUP_PATH/inc_base)
MYSQL_SOCK=/tmp/$(grep '^socket' $MYSQL_PATH/my.cnf|head -n1|rev|cut -d\/ -f1|rev)
LOG_NAME="$DB_NAME-$LOG_TIME.log"
[ ! -d $BACKUP_PATH ] && mkdir $BACKUP_PATH
[ ! -d $LOG_PATH ] && mkdir $LOG_PATH
mv $BACKUP_PATH/inc_base{,.back}

#检测今天是否已经存在备份,线上使用时需要把exit 3打开
count=$(ls $BACKUP_PATH|grep -c $(date +%Y-%m-%d))
if [ $count -ne 0 ] ;then
    echo "there has allready a tody's DB backup exist "
    cat >> $LOG_PATH/$LOG_NAME <<EOF
*******************************************************************
* there has allready a tody's DB backup exist                     *
* $LOG_TIME 已经备份,不需要再次执行                               *
*******************************************************************
EOF
#    exit 3
fi


function backup_increment(){
    innobackupex  --ibbackup=/usr/bin/xtrabackup_55 --incremental --slave-info --safe-slave-backup --parallel=$thread --defaults-file=$MYSQL_PATH/my.cnf --user=root --password=$PASSWD --socket=$MYSQL_SOCK --use-memory=${MEM}G $BACKUP_PATH --incremental-basedir=$BASE_DIR
}

backup_increment $MYSQL_PATH >> $LOG_PATH/$LOG_NAME 2>&1
BACKUP_OUT_DIR=$(grep 'Created backup directory' $LOG_PATH/$LOG_NAME|awk '{print $NF}')
#检查是否备份成功
grep Error $LOG_PATH/$LOG_NAME
result=$?
if [ $result -eq 0 ];then
##失败处理
    for user in $report_user
    do
        cat $LOG_PATH/$LOG_NAME|mail -s "Database $LOG_NAME backup error !!!!" $user@your_email.com
        echo "$BACKUP_OUT_DIR ------error and will be remove " >> $LOG_PATH/$LOG_NAME
        rm -fr $BACKUP_OUT_DIR
        mv $BACKUP_PATH/inc_base{.back,}
    done
else
#备份成功
    new_base_dir=$(ls -t $BACKUP_PATH|grep $(date +%Y)|head -n1)
    echo "$BACKUP_PATH/$new_base_dir" > $BACKUP_PATH/inc_base
    rm $BACKUP_PATH/inc_base.back
fi
