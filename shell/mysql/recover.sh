#!/bin/bash


cat <<EOF
============================================================================
如果你需要使用增量加全备份恢复数据到某一个增量备份的数据,务必先使用增量备份--incremental-dir将base_dir的数据恢复到该时刻!!!!!!!

当所有还原完毕后:
Note that the iblog* files will not be created by innobackupex, if you want
them to be created, use xtrabackup –prepare on the directory. Otherwise, the
files will be created by the server once started.
============================================================================
EOF

function error(){
  if [[ $# -lt 2 ]];then
    echo -e "Use:\n\t$0 base base_dir my.cnf(path)"
    echo -e "or Use:\n\t$0 increment base_dir (mysql's)my.cnf increment_dir(absolute_dir)"
    exit 3
  fi
}

BASE_PATH=$2
MY_CNF=$3
INC_PATH=$4

function base_recover(){
    innobackupex --apply-log --redo-only  --ibbackup=xtrabackup_55  --use-memory=4G   $BASE_PATH --defaults-file=$MY_CNF
}
function increment_recover(){
    innobackupex --apply-log --redo-only  --ibbackup=xtrabackup_55 --parallel=8  --use-memory=4G  $BASE_PATH  --incremental-dir=$INC_PATH --defaults-file=$MY_CNF
}

case $1 in
base)
    base_recover;
;;
increment)
    increment_recover;
;;
*)
    error;
;;
esac
