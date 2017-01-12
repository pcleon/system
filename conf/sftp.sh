if [ $# -ne 1 ];then
    echo "Usage: $0 username"
    exit 3
fi

[ -d /data/sftp ] || mkdir -p /data/sftp

user=$1
sftp_dir=/data/sftp/$user

useradd -m -G ftp -s /sbin/nologin $user
mkdir -p /home/$user/.ssh && chmod 700 /home/$user/.ssh
touch /home/$user/.ssh/authorized_keys  && chmod 600 /home/$user/.ssh/authorized_keys 
chown -R $user.$user /home/$user/.ssh

[ -d $sftp_dir ] || mkdir -p $sftp_dir 
mkdir $sftp_dir/upload && chown $user.$user $sftp_dir/upload

echo "$user:$user" |chpasswd
passwd -l $user

cat >/etc/ssh/sftp.42131<<EOF
#
Port 42131   
#ListenAddress     x.x.x.x
Protocol 2
SyslogFacility AUTHPRIV
RSAAuthentication yes
PubkeyAuthentication yes
AuthorizedKeysFile      .ssh/authorized_keys
PermitEmptyPasswords no
PasswordAuthentication no
ChallengeResponseAuthentication yes
GSSAPIAuthentication yes
GSSAPICleanupCredentials yes
UsePAM yes
AcceptEnv LANG LC_CTYPE LC_NUMERIC LC_TIME LC_COLLATE LC_MONETARY LC_MESSAGES
AcceptEnv LC_PAPER LC_NAME LC_ADDRESS LC_TELEPHONE LC_MEASUREMENT
AcceptEnv LC_IDENTIFICATION LC_ALL LANGUAGE
AcceptEnv XMODIFIERS
X11Forwarding yes
UseDNS no 

Subsystem       sftp    internal-sftp
#Match Group ftp
  ForceCommand internal-sftp
  ChrootDirectory /data/sftp/%u
  X11Forwarding no
  AllowTcpForwarding no

EOF

/usr/sbin/sshd -f /etc/ssh/sftp.42131 
