### 0.define section               #自定义宏段，这个不是必须的%define _prefix /home/service/cronolog

%define _sysconfdir %_prefix/etc

%define _localstatedir %_prefix/var

%define _sharedstatedir %_prefix/var/lib

### 1.The introduction section      #介绍区域段

#名字为tar包的名字

Name:           cronolog

#版本号

Version:        1.7.0

#释出号，也就是第几次制作rpm

Release:        beta

#软件包简介，最好不要超过50字符

Summary:        cronolog

#组名，可以通过less /usr/share/doc/rpm-x.x.x/GROUPS 选择合适组

Group:         Applications/System

#许可，GPL还是BSD等

License:        GPLv2

#可以写一个网址

URL:            http://cronolog.org/

#打包的人

Packager:       leon <wpctszz@qq.com>

#厂商

Vendor:         cronolog.org

#写正确的在SOURCE里面源码包的名字

#Source:        %{name}-%{version}.tar.gz

Source:         cronolog-1.7.0-beta.tar.gz

#定义用到的source，也就是你收集的，可以用宏来表示，也可以直接写名字，上面定义的内容都可以像上面那样引用

#如果需要补丁，依次写

#patch0:            a.patch

BuildRoot:      %_topdir/BUILDROOT

#这个是软件make install 的测试安装目录，也就是测试中的根，我们不用默认的，我们自定义，

#我们可以来观察生成了哪此文件，方便写file区域

#制作过程中用到的软件包

BuildRequires:  gcc,make

#软件运行需要的软件包，也可以指定最低版本如 bash >= 1.1.1

Requires:       pcre,pcre-devel,chkconfig

#软件包描述，尽情的写吧

%description

#描述内容

cronolog splite log



###  2.The Prep section 准备阶段,主要目的解压source并cd进去

#这个宏开始

%prep

#这个宏的作用静默模式解压并cd

%setup -q

#如果需要在这打补丁，依次写

# patch0 -p1



###  3.The Build Section 编译制作阶段，主要目的就是编译

#./configure也可以用%configure来替换

%build

%configure



#make后面的意思是：如果就多处理器的话make时并行编译

make %{?_smp_mflags}



###  4.Install section  安装阶段

%install

#先删除原来的安装的，如果你不是第一次安装的话

#rm -rf %{buildroot}

#rm -fr %{_buildrootdir}/%{name}-%{version}-%{release}.%{_arch}

#DESTDIR指定安装的目录，而不是真实的安装目录，%{buildroot}你应该知道是指的什么了

make DESTDIR=$RPM_BUILD_ROOT install

#make install DESTDIR=%{buildroot}



###  4.1 scripts section #没必要可以不写

#rpm安装前制行的脚本

%pre

#安装后执行的脚本

%post

ln -s %{_prefix}/sbin/cronolog /usr/local/bin/

#卸载前执行的脚本

%preun

rm -rf %{_prefix}

unlink /usr/local/bin/cronolog

#卸载后执行的脚本

%postun



###  5.clean section 清理段,删除buildroot

%clean



###  6.file section 要包含的文件

%files

#设定默认权限，如果下面没有指定权限，则继承默认

#用于定义软件包所包含的文件，分为三类--说明文档（doc），配置文件（config）及执行程序，还可定义文件存取权限，拥有者及组别。

   /home/service/cronolog/sbin/cronolog

   /home/service/cronolog/sbin/cronosplit

   /home/service/cronolog/share/info/cronolog.info

   /home/service/cronolog/share/info/dir

   /home/service/cronolog/share/man/man1/cronolog.1m

   /home/service/cronolog/share/man/man1/cronosplit.1m

#   /usr/sbin/cronolog

#   /usr/sbin/cronosplit

   /usr/share/info/cronolog.info.gz

#   /usr/share/info/dir

   /usr/share/man/man1/cronolog.1m.gz

   /usr/share/man/man1/cronosplit.1m.gz

  /usr/sbin/cronolog

%exclude  /usr/sbin/cronosplit

%exclude  /usr/share/info/dir



%defattr (-,root,root,0755)



#本段是修改日志段。你可以将软件的每次修改记录到这里，保存到发布的软件包中，以便查询之用。每一个修改日志都有这样一种格式：第一行是：* 星期 月 日 年 修改人电子信箱。其中：星期、月份均用英文形式的前3个字母，用中文会报错。接下来的行写的是修改了什么地方，可写多行。一般以减号开始，便于后续的查阅。

%changelog

