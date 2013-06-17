#!/bin/bash
if [ $# -ne 1 ];then
    echo -e "Use: \n\t $0 mysql_path "
    exit 3
fi

function back_full(){
    innobackupex --ibbackup=xtrabackup_55 --slave-info --safe-slave-backup --defaults-file=$MYSQL_PATH/my.cnf --user=root --password=$PASSWD --socket=$MYSQL_SOCK --rsync --use-memory=${MEM}G  $BACKUP_PATH
}


###for mysql
#Enter user who you want to mail
report_user=""
MYSQL_PATH=$1
MYSQL_SOCK=/tmp/$(grep '^socket' $MYSQL_PATH/my.cnf|head -n1|rev|cut -d\/ -f1|rev)
PASSWD=
#PASSWD=leon
MYSQL_USER=root
DB_NAME=$(basename $MYSQL_PATH)
BACKUP_PATH=/data/backup/$DB_NAME
LOG_PATH=/var/log/backup_mysql/full
MEM=4

[ ! -d $BACKUP_PATH ] && mkdir $BACKUP_PATH

mv $BACKUP_PATH/now_base{,.back}
LOG_TIME=$(date +%Y%m%d%H%M%S)
LOG_NAME="$DB_NAME-$LOG_TIME.log"
###备份开始执行
back_full >> $LOG_PATH/$LOG_NAME 2>&1
BACKUP_OUT_DIR=$(grep 'Created backup directory' $LOG_PATH/$LOG_NAME|awk '{print $NF}')
#检查是否备份成功
grep Error $LOG_PATH/$LOG_NAME
result=$?
if [ $result -eq 0 ];then
#备份失败
    for user in $report_user
    do
        cat $LOG_PATH/$LOG_NAME|mail -s "Database $LOG_NAME backup error !!!!" $user@your_email.com
        echo "$BACKUP_OUT_DIR ------error and will be remove " >> $LOG_PATH/$LOG_NAME
        rm -fr $BACKUP_OUT_DIR
        mv $BACKUP_PATH/now_base{.back,}
    done
else
#备份成功
    new_base_dir=$(ls -t $BACKUP_PATH|grep $(date +%Y)|head -n1)
    echo "$BACKUP_PATH/$new_base_dir" > $BACKUP_PATH/now_base
    echo "$BACKUP_PATH/$new_base_dir" > $BACKUP_PATH/inc_base
    rm $BACKUP_PATH/now_base.back
fi
