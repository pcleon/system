useradd -m -d /data/sftp -s /sbin/nologin -G ftp sftp
chmod 755 /data/sftp
chown root.root /data/sftp
mkdir /data/sftp/upload
chown sftp.sftp upload
echo 'sftp:sftp' |chpasswd

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
#Match User gzcb_repay
Match Group sftp
  ForceCommand internal-sftp
  ChrootDirectory %h
  X11Forwarding no
  AllowTcpForwarding no

EOF

/usr/sbin/sshd -f /etc/ssh/sftp.42131 
