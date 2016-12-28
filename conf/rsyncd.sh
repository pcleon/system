useradd -M -s /bin/false -G users up_file
mkdir -p /data/up_file ;chown up_file.users /data/up_file

cat >rsyncd.conf<<EOF 
uid = up_file 
gid = users
#gid = root
use chroot = no
hosts allow=*
max connections = 1000
syslog facility = local5
pid file = /var/run/rsyncd.pid
lock file = /var/run/rsync.lock
log file = /var/log/rsyncd.log
read only = no
write only = no
#hosts allow = x.x.x.x
[up_file]
      path = /data/up_file
      comment = office
      auth users = up_file
      secrets file = /etc/rsyncd.pwd
EOF

cat >rsyncd.pwd <<EOF
up_file:test
EOF

rsync --daemon --config=/etc/rsyncd.conf --port=12000
