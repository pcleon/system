Name:           scribed
Version:        0
Release:        1.mlssa
Summary:        scribed server
Group:          Applications/System
License:        GPLv2
URL:            https://github.com/facebook/scribe
Packager:       leon <wpctszz@qq.com>
Vendor:         https://github.com/facebook/scribe
Source:         scribed.tar.gz
BuildRoot:      %_topdir/BUILDROOT
#BuildRequires:
Requires:      python
%description
scribed  for collect log
%prep
%setup -q -n scribed
%build
mv scribed $RPM_BUILD_ROOT/home/service/
%install
%pre
%post
echo "load lib for scribe"
cat >>/etc/ld.so.conf.d/scribed.conf<<EOF
/home/service/scribed/lib
EOF
ldconfig
echo "done"
%preun
rm -f /etc/ld.so.conf.d/scribed.conf
ldconfig
%postun
%clean
%files
/home/service/scribed
%defattr (-,root,root,0755)
%changelog
