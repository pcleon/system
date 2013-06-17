Name:           scribelogVersion:        1
Release:        0
Summary:        scribelog
Group:          Applications/System
License:        GPLv2
URL:            http://else.org/scribelog
Packager:       leon <wpctszz@qq.com>
Vendor:         http://scribe/scribelog
Source:         scribelog.tar.gz
BuildRoot:      %_topdir/BUILDROOT
BuildRequires:  gcc,make
Requires:      python
%description
scribelog  for get log
%prep
%setup -q -n %{name}
%build
cp -r scribe_client $RPM_BUILD_ROOT/home/service/
%install
%pre
%post
%preun
%postun
%clean
%files
/home/service/scribe_client/*
%defattr (-,root,root,0755)
%changelog
