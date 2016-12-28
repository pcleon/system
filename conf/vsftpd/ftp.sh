cat >/etc/vsftpd/vconf/test<<EOF
local_root=/data/ftp/test
anonymous_enable=NO
write_enable=YES
anon_umask=022
anon_upload_enable=yes
anon_mkdir_write_enable=yes
idle_session_timeout=600
data_connection_timeout=120
max_clients=100
max_per_ip=50
local_max_rate=5000000
EOF

cat > /etc/vsftpd/vsftpd.conf<<EOF
listen=YES
anonymous_enable=NO
local_enable=YES
chroot_list_enable=NO
ascii_upload_enable=YES
ascii_download_enable=YES
pam_service_name=vsftpd
guest_enable=YES
guest_username=ftp
user_config_dir=/etc/vsftpd/vconf
xferlog_enable=YES
xferlog_std_format=YES
xferlog_file=/var/log/xferlog
dual_log_enable=YES
vsftpd_log_file=/var/log/vsftpd.log
EOF

cat >/etc/vsftpd/test<<EOF
test
test123
EOF

cd /etc/vsftpd/;  db_load -T -t hash -f user.txt user.db

cat >/etc/pam.d/vsftpd <<EOF
#%PAM-1.0
auth    sufficient      /lib64/security/pam_userdb.so db=/etc/vsftpd/user
account sufficient      /lib64/security/pam_userdb.so db=/etc/vsftpd/user
session    optional     pam_keyinit.so    force revoke
auth       required pam_listfile.so item=user sense=deny file=/etc/vsftpd/ftpusers onerr=succeed
auth       required pam_shells.so
auth       include  system-auth
account    include  system-auth
session    include  system-auth
session    required     pam_loginuid.so
EOF

mkdir -p /data/ftp/test
chown -R ftp.ftp /data/ftp
chmod 755 /data/ftp;chmod 755 /data/ftp/test
