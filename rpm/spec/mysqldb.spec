Name:           MySQLdb
Version:        1.3.0
Release:        pre
Summary:        MySQLdb
Group:         Applications/System
License:        GPLv2
URL:            http://MySQLdb.org/
Packager:       leon <wpctszz@qq.com>
Vendor:         MySQLdb
Source:         MySQLdb.tgz
BuildRoot:      %_topdir/BUILDROOT
BuildRequires:  python27,setuptools
Requires:       python27 >= 2.7.3, mysql-devel
%description
MySQLdb
%prep
%setup -q
%build
python setup.py build
%install
python setup.py install --single-version-externally-managed --root=$RPM_BUILD_ROOT
%pre
source /etc/profile
%post
%preun
%postun
%clean
%files
   /usr/local/lib/python2.7/site-packages/MySQL_python-1.3.0-py2.7.egg-info/PKG-INFO
   /usr/local/lib/python2.7/site-packages/MySQL_python-1.3.0-py2.7.egg-info/SOURCES.txt
   /usr/local/lib/python2.7/site-packages/MySQL_python-1.3.0-py2.7.egg-info/dependency_links.txt
   /usr/local/lib/python2.7/site-packages/MySQL_python-1.3.0-py2.7.egg-info/top_level.txt
   /usr/local/lib/python2.7/site-packages/_mysql.so
   /usr/local/lib/python2.7/site-packages/MySQLdb/*
%defattr (-,root,root,0755)
%changelog
