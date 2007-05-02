# compatability macros
%{?!mkrel:%define mkrel(c:) %{-c:0.%{-c*}.}%{!?_with_unstable:%(perl -e '$_="%{1}";m/(.\*)(\\d+)$/;$rel=${2}-1;re;print "$1$rel";').%{?subrel:%subrel}%{!?subrel:1}.%{?distversion:%distversion}%{?!distversion:%(echo $[%{mdkversion}/10])}}%{?_with_unstable:%{1}}%{?distsuffix:%distsuffix}%{?!distsuffix:mdk}}

%{?!_with_unstable: %{error:%(echo -e "\n\n\nYou are building package for a stable release, please see \nhttp://qa.mandriva.com/twiki/bin/view/Main/DistroSpecificReleaseTag\nif you think this is incorrect\n\n\n ")}%(sleep 2)}

# Example usage: %if %{defined with_foo} && %{undefined with_bar} ...
%define defined()  %{expand:%%{?%{1}:1}%%{!?%{1}:0}}
%define undefined()    %{expand:%%{?%{1}:0}%%{!?%{1}:1}}

# Shorthand for %{defined with_...}
%define with()     %{expand:%%{?with_%{1}:1}%%{!?with_%{1}:0}}
%define without()  %{expand:%%{?with_%{1}:0}%%{!?with_%{1}:1}}

# useful in descriptions
%define with_TXT()     %{expand:%%{?with_%{1}:with %{1}}%%{!?with_%{1}:without %{1}}}

# use bcond_with if default is disabled
# use bcond_without if default is enabled
%define bcond_with()       %{expand:%%{?_with_%{1}:%%global with_%{1} 1}}
%define bcond_without()    %{expand:%%{!?_without_%{1}:%%global with_%{1} 1}}

# Disabled if official version, enabled if snapshot
%bcond_with experimental

# call package postfix-experimental?
# it cannot be parallel installed anyway
%if %{with experimental}
%bcond_without parallel
%else
%bcond_with parallel
%endif

%define pname		postfix
%define pver		2.4.1
# from src/global/mail_version.h
%define releasedate	20070130
%define rel		1

%if ! %{with experimental}
%define distver		%pver
%define distverdot	%pver
%define ftp_directory	official
%else
%define distver		%pver-%releasedate
%define distverdot	%pver.%releasedate
%define ftp_directory	experimental
%endif

# MAINTAINER, ATTENTION
# If the alternatives scheme is ever changed, please check the
# postfix init script as it has a fix for a previous alternatives
# problem outlined here: http://archives.mandrivalinux.com/cooker/2005-07/msg01012.php
%define alternatives 	1
%define alternatives_install_cmd update-alternatives --install %{_sbindir}/sendmail sendmail-command %{_sbindir}/sendmail.postfix 30 --slave %{_prefix}/lib/sendmail sendmail-command-in_libdir %{_sbindir}/sendmail.postfix

%if %alternatives
%define post_install_parameters	daemon_directory=%{_libdir}/postfix command_directory=%{_sbindir} queue_directory=%{queue_directory} sendmail_path=%{_sbindir}/sendmail.postfix newaliases_path=%{_bindir}/newaliases mailq_path=%{_bindir}/mailq mail_owner=postfix setgid_group=%{maildrop_group} manpage_directory=%{_mandir} readme_directory=%{_docdir}/%name-%version/README_FILES html_directory=%{_docdir}/%name-%version/html 
%else
%define post_install_parameters	daemon_directory=%{_libdir}/postfix command_directory=%{_sbindir} queue_directory=%{queue_directory} sendmail_path=%{_sbindir}/sendmail newaliases_path=%{_bindir}/newaliases mailq_path=%{_bindir}/mailq mail_owner=postfix setgid_group=%{maildrop_group} manpage_directory=%{_mandir} readme_directory=%{_docdir}/%name-%version/README_FILES html_directory=%{_docdir}/%name-%version/html 
%endif

# use bcond_with if default is disabled
# use bcond_without if default is enabled
%bcond_without dynamicmaps

%bcond_without ldap
%bcond_without mysql
%bcond_without pgsql
%bcond_without pcre
%bcond_without sasl
%bcond_without tls
%bcond_without ipv6
%bcond_with cdb
# XXX - andreas - currently (pfix 2.2.4) not applying
# and no new version was found
#bcond_with pam
%bcond_with multiline
%bcond_with VDA
%bcond_without chroot
%bcond_with multi_instance

# Postfix requires one exlusive uid/gid and a 2nd exclusive gid for its own use.
%define maildrop_group	postdrop
%define queue_directory	%{_var}/spool/postfix

%if %{with dynamicmaps}
%define dynmap_add_cmd() FILE=%{_sysconfdir}/postfix/dynamicmaps.cf; if ! grep -q "^%{1}[[:space:]]" ${FILE}; then echo "%{1}	%{_libdir}/postfix/dict_%{1}.so	dict_%{1}_open" >> ${FILE}; fi
%define dynmap_rm_cmd() FILE=%{_sysconfdir}/postfix/dynamicmaps.cf; if [ $1 = 0 -a -s $FILE ]; then  cp -p ${FILE} ${FILE}.$$; grep -v "^%{1}[[:space:]]" ${FILE}.$$ > ${FILE}; rm -f ${FILE}.$$; fi
%endif

%if ! %{with parallel}
Name:		%{pname}
Version:	%{distverdot}
Release:	%mkrel %{rel}
Conflicts:	%{pname}-experimental
%else
Name:		%{pname}-experimental
Version:	%{pver}
Release:	%mkrel -c %{releasedate} %{rel}
Provides:	%{pname}
Conflicts:	%{pname}
%endif
Summary:	Postfix Mail Transport Agent
Epoch:		1
URL:		http://www.postfix.org/
Source0: 	ftp://ftp.porcupine.org/mirrors/postfix-release/%{ftp_directory}/%{pname}-%{distver}.tar.gz
Source1: 	ftp://ftp.porcupine.org/mirrors/postfix-release/%{ftp_directory}/%{pname}-%{distver}.tar.gz.sig
Source2: 	postfix-main.cf
# MAINTAINER, ATTENTION
# If the alternatives scheme is ever changed, please check the postfix
# init script as it has a fix for a previous alternatives problem outlined here:
# http://archives.mandrivalinux.com/cooker/2005-07/msg01012.php
# Also, this init script recreates /usr/bin/rmail if needed:
# http://archives.mandrivalinux.com/cooker/2005-07/msg01691.php
Source3: 	postfix-etc-init.d-postfix
Source4:	postfix-etc-pam.d-smtp
Source5:	postfix-aliases
Source6:	postfix-ip-up
Source7:	postfix-ip-down
Source8:	postfix-ifup-d
Source10:	postfix-README.MDK
Source11:	postfix-README.MDK.update
#Source11:	http://www.comedia.it/~bluca/postfix/CYRUS_README
Source12:	postfix-bash-completion
Source13:	http://www.seaglass.com/postfix/faq.html
Source14:	postfix-chroot.sh
Source15:	postfix-smtpd.conf

# Simon J. Mudd stuff
Source21:	ftp://ftp.wl0.org/postfinger/postfinger-1.30

# Jim Seymour stuff
Source25:	http://jimsun.LinxNet.com/misc/postfix-anti-UCE.txt
Source26:	http://jimsun.LinxNet.com/misc/header_checks.txt
Source27:	http://jimsun.LinxNet.com/misc/body_checks.txt

# Dynamic map patch taken from debian's package
Patch0:		postfix-2.3.1-dynamicmaps.patch

Patch1:		postfix-2.3.2-mdkconfig.patch
Patch2:		postfix-alternatives-mdk.patch
Patch3:		postfix-smtp_sasl_proto.c.patch

# Shamelessy stolen from debian
Patch6:		postfix-2.2.4-smtpstone.patch

# applied if %with pam
# originally from http://d.scn.ru/proj/postfix/dict_pam/
Patch7:		postfix-2.0.16-20030921.pam.patch

# applied if %with multiline
Patch8: ftp://ftp.wl0.org/SOURCES/postfix-2.3.2-multiline-greeting.patch

# applied if %with vda
# http://web.onda.com.br/nadal/
Patch9: http://web.onda.com.br/nadal/postfix/VDA/postfix-2.3.3-vda.patch

# from postfix-users ml, adapted to 2.3
Patch10:	postfix-2.3.2-sasl_logging.patch

# applied if %with multi_instance
# originally http://www.stahl.bau.tu-bs.de/~hildeb/postfix/duchovni/multi_instance.gz
# if you rediff this one from upstream remember to modify post-install to symlink
# dynamicmaps.cf
Patch23:	postfix-multi_instance.patch

License:	IBM Public License
Group:		System/Servers
Provides:	mail-server
Provides:	sendmail-command
# http://archives.mandrivalinux.com/cooker/2005-06/msg01987.php
Requires(post): chkconfig, initscripts, coreutils
Requires(post): sysklogd, fileutils
Requires(pre,post,postun,preun): rpm-helper >= 0.3
# Requiring "ed" twice due to http://archives.mandrivalinux.com/cooker/2005-06/msg00109.php
Requires(post): ed
Requires:		ed
# ed is used in %%install
BuildRequires: 	ed
Requires(pre):	sed
Requires:		sed
%if %alternatives
Requires(post):		update-alternatives
Requires(preun):	update-alternatives
%else
Conflicts:	sendmail exim qmail
%endif
BuildRequires:	db4-devel, gawk, perl-base, sed, ed
BuildRequires:	html2text
BuildRoot:	%{_tmppath}/%{name}-%{pver}-%{rel}-root

%if %{with sasl}
BuildRequires:	libsasl-devel >= 2.0
%endif

%if %{with tls}
BuildRequires:	openssl-devel >= 0.9.7
%endif

%if %{with cdb}
BuildRequires: libtinycdb-devel
%endif

%if %{with dynamicmaps}
%define libname %mklibname postfix 1
Requires:	%{libname} = %epoch:%version-%release
Requires(post):	%{libname} = %epoch:%version-%release
# versionless require or we will break upgrades
Requires(preun):	%{libname}
%endif

%description
Postfix is a Mail Transport Agent (MTA), supporting LDAP, SMTP AUTH (SASL),
TLS and running in a chroot environment.

Postfix is Wietse Venema's mailer that started life as an alternative 
to the widely-used Sendmail program.
Postfix attempts to be fast, easy to administer, and secure, while at 
the same time being sendmail compatible enough to not upset existing 
users. Thus, the outside has a sendmail-ish flavor, but the inside is 
completely different.
This software was formerly known as VMailer. It was released by the end
of 1998 as the IBM Secure Mailer. From then on it has lived on as Postfix. 

PLEASE READ THE %{_defaultdocdir}/%{name}-%{version}/README.MDK FILE.

This rpm supports different build time options, to enable or disable these
features you must rebuild the source rpm using the --with ... or --without ...
rpm option.
Currently postfix has been built with:

	Smtpd multiline greeting: --%{with_TXT multiline}
	Virtual Delivery Agent: --%{with_TXT VDA}
	Munge bare CR: --%{with_TXT barecr}
	TLS support: --with tls %{with_TXT_tls}
	IPV6 support: --with IPV6 %{with_TXT_ipv6}
	CDB support: --%{with_TXT cdb}
	Chroot by default: --%{with_TXT chroot}

%if %{with dynamicmaps}
%package -n %{libname}
Summary:	Shared libraries required to run Postfix
Group:		System/Servers

%description -n %{libname}
This package contains shared libraries used by Postfix.

%if %{with ldap}
%package ldap
Summary:	LDAP map support for Postfix
Group:		System/Servers
BuildRequires:	openldap-devel >= 2.1
Requires:	%name = %epoch:%version-%release

%description ldap
This package provides support for LDAP maps in Postfix.
%endif

%if %{with pcre}
%package pcre
Summary:	PCRE map support for Postfix
Group:		System/Servers
BuildRequires:	pcre-devel
Requires:	%name = %epoch:%version-%release

%description pcre
This package provides support for PCRE (perl compatible regular expression)
maps in Postfix.
%endif

%if %{with mysql}
%package mysql
Summary:	MYSQL map support for Postfix
Group:		System/Servers
BuildRequires:	MySQL-devel
Requires:	%name = %epoch:%version-%release

%description mysql
This package provides support for MYSQL maps in Postfix.
%endif

%if %{with pgsql}
%package pgsql
Summary:	Postgres SQL map support for Postfix
Group:		System/Servers
# From the release notes of postfix-2.2.11:
# The PostgreSQL client was updated after major database API changes
# in response to PostgreSQL security issues. This breaks support for
# PGSQL versions prior to 8.1.4, 8.0.8, 7.4.13, and 7.3.15. Support
# for these requires major code changes which are not possible in a
# stable release.
BuildRequires:	postgresql-devel >= 8.1.4
Requires:	%name = %epoch:%version-%release

%description pgsql
This package provides support for Postgres SQL maps in Postfix.
%endif

%if %{with pam}
%package pam
Summary:	PAM map support for Postfix
Group:		System/Servers
BuildRequires:	pam-devel
Requires:	%name = %epoch:%version-%release

%description pam
This package provides support for PAM maps in Postfix.
%endif

%endif
# dynamicmaps

%prep
%setup -n %{pname}-%{distver} -q

%if %{with dynamicmaps}
%patch0 -p1 -b .dynamic 
cat > conf/dynamicmaps.cf <<EOF
# Postfix dynamic maps configuration file.
#
# The first match found is the one that is used.  Wildcards are not
# supported.
#
#type  location of .so file            name of open function
#====  =============================   =====================
EOF
%endif

# no backup files here, otherwise they get included in %%doc
%patch1 -p1
mkdir -p conf/dist
mv conf/main.cf conf/dist
cp %{SOURCE2} conf/main.cf
# ugly hack for 32/64 arches
if [ %{_lib} != lib ]; then
	ed conf/main.cf <<-EOF || exit 1
	,s/\/lib\//\/%{_lib}\//g
	w
	q
EOF
fi

%if %alternatives
%patch2 -p1 -b .alternatives
%endif

# XXX - andreas - still needed/desired?
# ref: http://archives.neohapsis.com/archives/postfix/2001-05/1485.html
#%%patch3 -p1 -b .auth

%patch6 -p1 -b .smtpstone 

# Apply PAM Patch
%if %{with pam}
%patch7 -p1 -b .pam
#rm -f README_FILES/PAM_README.pam
%endif

# Apply SMTPD Multiline greeting patch
%if %{with multiline}
%patch8 -p1 -b .multiline
%endif

%if %{with VDA}
%patch9 -p1 -b .vda
%endif

# doesn't build yet
#%patch10 -p1 -b .sasl_logging

%if %{with multi_instance}
%patch23 -p1 -b .multi_instance
%endif

install -m644 %{SOURCE10} README.MDK
install -m644 %{SOURCE11} README.MDK.update
#install -m644 %{SOURCE11} README_FILES/CYRUS_README
install -m644 %{SOURCE13} postfix-users-faq.html

mkdir UCE
install -m644 %{SOURCE25} UCE
install -m644 %{SOURCE26} UCE
install -m644 %{SOURCE27} UCE

%if %{with chroot}
cp -p conf/master.cf conf/master.cf.chroot
awk -v NEVER_CHROOT_PROGRAM='^(proxymap|local|pipe|virtual|spawn)$' \
	-v NEVER_CHROOT_SERVICE='^cyrus$' '
		BEGIN                   { IFS="[ \t]+"; OFS="\t"; }
		/^#/                    { print; next; }
		/^ /                    { print; next; }
		$1 ~ NEVER_CHROOT_SERVICE    { print; next; }
		$8 ~ NEVER_CHROOT_PROGRAM    { print; next; }
		$5 == "n"               { $5="y"; print $0; next; }
								{ print; }
	' conf/master.cf.chroot > conf/master.cf
%endif

# use sed to fix mantools/postlink for our non posix sed
#cp -p mantools/postlink mantools/postlink.posix
#sed -e 's/\[\[:<:\]\]/\\</g; s/\[\[:>:\]\]/\\>/g' mantools/postlink.posix > mantools/postlink
# XXX - andreas - original postlink with perl is segfaulting
cp -p mantools/postlink.sed mantools/postlink.posix
sed -e 's/\[\[:<:\]\]/\\</g; s/\[\[:>:\]\]/\\>/g' mantools/postlink.posix > mantools/postlink

%build
%serverbuild
CCARGS="-fstack-protector"
AUXLIBS=

%ifarch s390 s390x ppc
CCARGS="${CCARGS} -fsigned-char"
%endif

%if %{with dynamicmaps}
# the patch is mixed with SDBM support :(
  CCARGS="${CCARGS} -DHAS_SDBM -DHAS_DLOPEN -DHAS_SHL_LOAD"
%endif

%if %{with ldap}
  CCARGS="${CCARGS} -DHAS_LDAP"
%if ! %{with dynamicmaps}
  AUXLIBS="${AUXLIBS} -lldap -llber"
%endif
%endif
%if %{with pcre}
  CCARGS="${CCARGS} -DHAS_PCRE"
%if ! %{with dynamicmaps}
  AUXLIBS="${AUXLIBS} -lpcre"
%endif
%endif
%if %{with mysql}
  CCARGS="${CCARGS} -DHAS_MYSQL -I/usr/include/mysql"
%if ! %{with dynamicmaps}
  AUXLIBS="${AUXLIBS} -lmysqlclient"
%endif
%endif
%if %{with pgsql}
  CCARGS="${CCARGS} -DHAS_PGSQL -I/usr/include/pgsql"
%if ! %{with dynamicmaps}
  AUXLIBS="${AUXLIBS} -lpq"
%endif
%endif
%if %{with sasl}
  CCARGS="${CCARGS} -DUSE_SASL_AUTH -DUSE_CYRUS_SASL -I/usr/include/sasl"
  AUXLIBS="${AUXLIBS} -lsasl2"
%endif
%if ! %{with ipv6}
  CCARGS="${CCARGS} -DNO_IPV6"
%endif
%if %{with tls}
  CCARGS="${CCARGS} -DUSE_TLS -I/usr/include/openssl"
  AUXLIBS="${AUXLIBS} -lssl -lcrypto"
%endif
%if %{with cdb}
  CCARGS="${CCARGS} -DHAS_CDB"
  AUXLIBS="${AUXLIBS} -lcdb"
%endif
%if %{with pam}
  CCARGS="${CCARGS} -DHAS_PAM"
%endif

export CCARGS AUXLIBS
make -f Makefile.init makefiles

unset CCARGS AUXLIBS
make DEBUG="" OPT="$RPM_OPT_FLAGS"
make manpages

%if %{with dynamicmaps}
for i in lib/*.a; do
	j=${i#lib/lib}
	ln -s ${i#lib/} lib/libpostfix-${j%.a}.so.1
done

# generate main.cf.default here, since in make it will fail
cat > conf/main.cf.default << EOF
# DO NOT EDIT THIS FILE. EDIT THE MAIN.CF FILE INSTEAD. THE
# TEXT HERE JUST SHOWS DEFAULT SETTINGS BUILT INTO POSTFIX.
#
EOF
LD_LIBRARY_PATH=$PWD/lib${LD_LIBRARY_PATH:+:}${LD_LIBRARY_PATH} \
	./src/postconf/postconf -d | \
	egrep -v '^(myhostname|mydomain|mynetworks) ' >> conf/main.cf.default
%endif

# add correct parameters to main.cf.dist
LD_LIBRARY_PATH=$PWD/lib${LD_LIBRARY_PATH:+:}${LD_LIBRARY_PATH} \
	./src/postconf/postconf -c ./conf/dist -e \
	%post_install_parameters
mv conf/dist/main.cf conf/main.cf.dist

%install
rm -fr %buildroot

# install postfix into the build root
LD_LIBRARY_PATH=$PWD/lib${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH} \
sh postfix-install -non-interactive \
	install_root=%buildroot \
	config_directory=%{_sysconfdir}/postfix \
	%post_install_parameters \
	|| exit 1

%if %{with dynamicmaps}
for i in lib/*.a; do
	j=${i#lib/lib}
	install $i %{buildroot}%{_libdir}/libpostfix-${j%.a}.so.1
done
%endif

# rpm %%doc macro wants to take his files in buildroot
rm -fr DOC
mkdir DOC
mv %buildroot%{_docdir}/%name-%version/html DOC/html
mv %buildroot%{_docdir}/%name-%version/README_FILES DOC/README_FILES

# for sasl configuration
/bin/mkdir -p %buildroot%{_sysconfdir}/sasl2
cp %{SOURCE15} %buildroot%{_sysconfdir}/sasl2/smtpd.conf

# This installs into the /etc/rc.d/init.d directory
/bin/mkdir -p %buildroot%{_initrddir}
install -c %{SOURCE3} %buildroot%{_initrddir}/postfix
/bin/mkdir -p %buildroot%{_sysconfdir}/pam.d
install -c %{SOURCE4} %buildroot%{_sysconfdir}/pam.d/smtp

mkdir -p %buildroot%{_sysconfdir}/ppp/ip-{up,down}.d
mkdir -p %buildroot%{_sysconfdir}/sysconfig/network-scripts/ifup.d
install -c %{SOURCE6} %buildroot%{_sysconfdir}/ppp/ip-up.d/postfix
install -c %{SOURCE7} %buildroot%{_sysconfdir}/ppp/ip-down.d/postfix
install -c %{SOURCE8} %buildroot%{_sysconfdir}/sysconfig/network-scripts/ifup.d/postfix
touch %buildroot%{_sysconfdir}/sysconfig/postfix

# this is used by some examples (cyrus)
mkdir -p %buildroot%{queue_directory}/extern

install -c auxiliary/rmail/rmail %buildroot%{_bindir}/rmail

# copy new aliases files and generate a ghost aliases.db file
cp -f %{SOURCE5} %buildroot%{_sysconfdir}/postfix/aliases
chmod 644 %buildroot%{_sysconfdir}/postfix/aliases
touch %buildroot%{_sysconfdir}/postfix/aliases.db

# install chroot script and postfinger
install -m 0755 %{SOURCE14} %buildroot%{_sbindir}/postfix-chroot.sh
install -m 0755 %{SOURCE21} %buildroot%{_sbindir}/postfinger

# install qshape
install -m755 auxiliary/qshape/qshape.pl %buildroot%{_sbindir}/qshape
cp man/man1/qshape.1 %buildroot%{_mandir}/man1/qshape.1

# RPM compresses man pages automatically.
# - Edit postfix-files to reflect this, so post-install won't get confused
#   when called during package installation.
ed %buildroot%{_sysconfdir}/postfix/postfix-files <<-EOF || exit 1
	,s/\(\/man[158]\/.*\.[158]\):/\1.bz2:/
	w
	q
EOF

%if %{with dynamicmaps}
# remove files that are not in the main package
ed %buildroot%{_sysconfdir}/postfix/postfix-files <<-EOF || exit 1
	g/dict_ldap.so/d
	g/dict_pam.so/d
	g/dict_pcre.so/d
	g/dict_mysql.so/d
	g/dict_pgsql.so/d
	w
	q
EOF
%endif

# remove sample_directory from main.cf (#15297)
# the default is /etc/postfix
sed -i "/^sample_directory/d" %{buildroot}%{_sysconfdir}/postfix/main.cf

%if %{with multi_instance}
cat > %buildroot%{_sysconfdir}/postfix/initial-main.cf << EOF
# SAFETY CATCH
#
# A stock main.cf will not start automatically.
# Comment out the setting below after changing main.cf to suit your needs.
#
disable_start = yes

EOF
cat %buildroot%{_sysconfdir}/postfix/main.cf >> %buildroot%{_sysconfdir}/postfix/initial-main.cf

# comment inet daemons in initial-master.cf
ed %buildroot%{_sysconfdir}/postfix/initial-master.cf <<-EOF || exit 1
	,s/^\([^#[:space:]]\+[[:space:]]\+inet[[:space:]]\+\)/#\1/
	w
	q
EOF
%endif


%pre
%_pre_useradd postfix %{queue_directory} /bin/false
%_pre_groupadd %{maildrop_group} postfix
if [ -e /var/lib/rpm/alternatives/mta ]; then
	/usr/sbin/update-alternatives --remove mta %{_sbindir}/sendmail.postfix
	echo
	echo "============================================================================"
	echo "WARNING"
	echo
	echo "The old \"mta-*\" alternatives have been removed."
	echo "After this upgrade, postfix may be partially broken due to an incorrect"
	echo "triggerpostun in previous packages. If there is no %{_bindir}/mailq,"
	echo "for example, then this is the case and you should keep reading."
	echo
	echo "To partially fix the problem, please restart the service after this"
	echo "upgrade is finished (even if it was already restarted during the upgrade)."
	echo
	echo "The init script will correct most of the broken symbolic links, but the"
	echo "following manpages will not be accessible: mailq(1), newaliases(1) and"
	echo "aliases(5)."
	echo
	echo "A reinstallation of the postfix package (or any further upgrade) will fix"
	echo "all issues."
	echo
	echo "See the http://archives.mandrivalinux.com/cooker/2005-07/msg01012.php thread"
	echo "for a more detailed explanation."
	echo "============================================================================"
	echo
fi
# disable chroot of spawn service in /etc/sysconfig/postfix, but do it only once and only if user did not
# modify /etc/sysconfig/postfix manually
if grep -qs "^NEVER_CHROOT_PROGRAM='^(proxymap|local|pipe|virtual)$'$" /etc/sysconfig/postfix; then
	if ! grep -qs "^NEVER_CHROOT_PROGRAM='^(proxymap|local|pipe|virtual|spawn)$'$" /usr/sbin/postfix-chroot.sh; then
		perl -pi -e "s/^NEVER_CHROOT_PROGRAM=.*\$/NEVER_CHROOT_PROGRAM=\'^(proxymap|local|pipe|virtual|spawn)\\\$\'/" /etc/sysconfig/postfix
	fi
fi
	
%post
# we don't have these maps anymore as separate packages/plugins:
# cidr, tcp and sdbm
if [ "$1" -eq "2" ]; then
	sed -i "/^cidr/d;/^sdbm/d;/^tcp/d" %{_sysconfdir}/postfix/dynamicmaps.cf
fi

# upgrade configuration files if necessary
sh %{_sysconfdir}/postfix/post-install \
	config_directory=%{_sysconfdir}/postfix \
	%post_install_parameters \
	upgrade-package

# move previous sasl configuration files to new location if applicable
# have to go through many loops to prevent damaging user configuration
saslpath=`postconf -h smtpd_sasl_path`
if [ "${saslpath}" != "${saslpath##*:}" -o "${saslpath}" != "${saslpath##*/usr/lib}" ]; then
	postconf -e smtpd_sasl_path=smtpd
fi

for old_smtpd_conf in /etc/postfix/sasl/smtpd.conf %{_libdir}/sasl2/smtpd.conf; do
	if [ -e ${old_smtpd_conf} ]; then
		if ! grep -qsve '^\(#.*\|[[:space:]]*\)$' /etc/sasl2/smtpd.conf; then
			# /etc/sasl2/smtpd.conf missing or just comments
			if [ -s /etc/sasl2/smtpd.conf ] && [ ! -e /etc/sasl2/smtpd.conf.rpmnew -o /etc/sasl2/smtpd.conf -nt /etc/sasl2/smtpd.conf.rpmnew ];then
				mv /etc/sasl2/smtpd.conf /etc/sasl2/smtpd.conf.rpmnew
			fi
			mv ${old_smtpd_conf} /etc/sasl2/smtpd.conf
		else
			echo "warning: existing ${old_smtpd_conf} will be ignored"
		fi
	fi
done

if [ -e /etc/sysconfig/postfix ]; then
	%{_sbindir}/postfix-chroot.sh -q update
%if %{with chroot}
else
	%{_sbindir}/postfix-chroot.sh -q enable
%endif
fi
%_post_service postfix

%if %alternatives
%{alternatives_install_cmd}
%endif


%triggerin -- glibc setup nss_ldap nss_db samba-winbind nss_wins samba2-winbind nss_wins2 samba3-winbind nss_wins3
# Generate chroot jails on the fly when needed things are installed/upgraded
%{_sbindir}/postfix-chroot.sh -q update

%preun
rmqueue() {
	[ $2 -gt 0 ] || return
	local i
	for i in 0 1 2 3 4 5 6 7 8 9 A B C D E F; do
		if [ -d $1/$i ]; then
			rmqueue $1/$i $(( $2 - 1 ))
			rm -f $1/$i/*
			rmdir $1/$i
		fi
	done
}

# selectively remove the queue directory structure
queue_directory_remove () {
# first remove the "queues"
local IFS=', '
for dir in `%{_sbindir}/postconf -h hash_queue_names`; do
	test -d $dir && rmqueue %{queue_directory}/$dir `%{_sbindir}/postconf -h hash_queue_depth`
done

# now remove the other directories
for dir in corrupt maildrop pid private public trace; do
	test -d $dir && /bin/rm -f $dir/*
done
}

%_preun_service postfix

if [ $1 = 0 ]; then
%if %alternatives
	/usr/sbin/update-alternatives --remove sendmail-command %{_sbindir}/sendmail.postfix
%endif

	# Clean up chroot environment and spool directory
	%{_sbindir}/postfix-chroot.sh -q remove
	cd %{queue_directory} && queue_directory_remove || true
fi

%postun
%_postun_userdel postfix
%_postun_groupdel %{maildrop_group}

%clean
rm -rf %buildroot

%files
%defattr(-, root, root, 755)
%dir %{_sysconfdir}/postfix
%config(noreplace) %{_sysconfdir}/sasl2/smtpd.conf
%{_sysconfdir}/postfix/postfix-script
%{_sysconfdir}/postfix/post-install
%{_sysconfdir}/postfix/postfix-files
%config(noreplace) %{_sysconfdir}/postfix/main.cf
# http://archives.mandrivalinux.com/cooker/2005-07/msg01109.php
%{_sysconfdir}/postfix/main.cf.dist
%{_sysconfdir}/postfix/main.cf.default
%{_sysconfdir}/postfix/bounce.cf.default
%config(noreplace) %{_sysconfdir}/postfix/master.cf
%config(noreplace) %{_sysconfdir}/postfix/access
%config(noreplace) %{_sysconfdir}/postfix/aliases
%ghost %{_sysconfdir}/postfix/aliases.db
%config(noreplace) %{_sysconfdir}/postfix/canonical
%config(noreplace) %{_sysconfdir}/postfix/generic
%config(noreplace) %{_sysconfdir}/postfix/header_checks
%config(noreplace) %{_sysconfdir}/postfix/relocated
%config(noreplace) %{_sysconfdir}/postfix/transport
%config(noreplace) %{_sysconfdir}/postfix/virtual
%{_sysconfdir}/postfix/makedefs.out
%if %{with dynamicmaps}
%config(noreplace) %{_sysconfdir}/postfix/dynamicmaps.cf
%endif
%if %{with multi_instance}
%{_sysconfdir}/postfix/initial-main.cf
%{_sysconfdir}/postfix/initial-master.cf
%endif

%attr(0755, root, root) %{_initrddir}/postfix
%attr(0644, root, root) %config(noreplace) %{_sysconfdir}/pam.d/smtp
%attr(0755, root, root) %config(noreplace) %{_sysconfdir}/ppp/ip-up.d/postfix
%attr(0755, root, root) %config(noreplace) %{_sysconfdir}/ppp/ip-down.d/postfix
%attr(0755, root, root) %config(noreplace) %{_sysconfdir}/sysconfig/network-scripts/ifup.d/postfix
%ghost %{_sysconfdir}/sysconfig/postfix

# For correct directory permissions check postfix-install script
%dir %{queue_directory}
%dir %attr(0700, postfix, root) %{queue_directory}/active
%dir %attr(0700, postfix, root) %{queue_directory}/bounce
%dir %attr(0700, postfix, root) %{queue_directory}/corrupt
%dir %attr(0700, postfix, root) %{queue_directory}/defer
%dir %attr(0700, postfix, root) %{queue_directory}/deferred
%dir %attr(0700, postfix, root) %{queue_directory}/flush
%dir %attr(0700, postfix, root) %{queue_directory}/hold
%dir %attr(0700, postfix, root) %{queue_directory}/incoming
%dir %attr(0700, postfix, root) %{queue_directory}/private
%dir %attr(0700, postfix, root) %{queue_directory}/trace
%dir %attr(0730, postfix, %{maildrop_group}) %{queue_directory}/maildrop
%dir %attr(0710, postfix, %{maildrop_group}) %{queue_directory}/public
%dir %attr(0755, root, root) %{queue_directory}/pid
%dir %attr(0755, root, root) %{queue_directory}/extern

%doc AAAREADME
%doc US_PATENT_6321267
%doc examples/smtpd-policy
%doc COMPATIBILITY
%doc COPYRIGHT
%doc HISTORY
%doc LICENSE
%doc PORTING
%doc RELEASE_NOTES*
%doc IPv6-ChangeLog
%doc TLS_*
#doc html
%doc DOC/html
%doc DOC/README_FILES
%doc README.MDK README.MDK.update
%doc postfix-users-faq.html
%doc UCE

%dir %{_libdir}/postfix
%attr(0755, root, root) %{_libdir}/postfix/bounce
%attr(0755, root, root) %{_libdir}/postfix/cleanup
%attr(0755, root, root) %{_libdir}/postfix/discard
%attr(0755, root, root) %{_libdir}/postfix/error
%attr(0755, root, root) %{_libdir}/postfix/flush
%attr(0755, root, root) %{_libdir}/postfix/lmtp
%attr(0755, root, root) %{_libdir}/postfix/local
%attr(0755, root, root) %{_libdir}/postfix/master
%attr(0755, root, root) %{_libdir}/postfix/nqmgr
%attr(0755, root, root) %{_libdir}/postfix/oqmgr
%attr(0755, root, root) %{_libdir}/postfix/pickup
%attr(0755, root, root) %{_libdir}/postfix/pipe
%attr(0755, root, root) %{_libdir}/postfix/proxymap
%attr(0755, root, root) %{_libdir}/postfix/qmgr
%attr(0755, root, root) %{_libdir}/postfix/qmqpd
%attr(0755, root, root) %{_libdir}/postfix/scache
%attr(0755, root, root) %{_libdir}/postfix/showq
%attr(0755, root, root) %{_libdir}/postfix/smtp
%attr(0755, root, root) %{_libdir}/postfix/smtpd
%attr(0755, root, root) %{_libdir}/postfix/spawn
%attr(0755, root, root) %{_libdir}/postfix/trivial-rewrite
%attr(0755, root, root) %{_libdir}/postfix/virtual
%attr(0755, root, root) %{_libdir}/postfix/tlsmgr
%attr(0755, root, root) %{_libdir}/postfix/anvil
%attr(0755, root, root) %{_libdir}/postfix/verify

%attr(0755, root, root) %{_sbindir}/postalias
%attr(0755, root, root) %{_sbindir}/postcat
%attr(0755, root, root) %{_sbindir}/postconf
%attr(2755,root,%{maildrop_group}) %{_sbindir}/postdrop
%attr(2755,root,%{maildrop_group}) %{_sbindir}/postqueue
%attr(0755, root, root) %{_sbindir}/postfix
%attr(0755, root, root) %{_sbindir}/postkick
%attr(0755, root, root) %{_sbindir}/postlock
%attr(0755, root, root) %{_sbindir}/postlog
%attr(0755, root, root) %{_sbindir}/postmap
%attr(0755, root, root) %{_sbindir}/postsuper

%attr(0755, root, root) %{_sbindir}/qmqp-sink
%attr(0755, root, root) %{_sbindir}/qmqp-source
%attr(0755, root, root) %{_sbindir}/smtp-sink
%attr(0755, root, root) %{_sbindir}/smtp-source

%attr(0755, root, root) %{_sbindir}/postfinger
%attr(0755, root, root) %{_sbindir}/postfix-chroot.sh
%attr(0755, root, root) %{_sbindir}/qshape

%if %alternatives
%attr(0755, root, root) %{_sbindir}/sendmail.postfix
%else
%attr(0755, root, root) %{_sbindir}/sendmail
%endif
%attr(0755, root, root) %{_bindir}/mailq
%attr(0755, root, root) %{_bindir}/newaliases
%attr(0755, root, root) %{_bindir}/rmail

%{_mandir}/*/*

%if %{with dynamicmaps}
%files -n %{libname}
%defattr(755, root, root)
%attr(0755, root, root) %{_libdir}/libpostfix-dns.so.1
%attr(0755, root, root) %{_libdir}/libpostfix-global.so.1
%attr(0755, root, root) %{_libdir}/libpostfix-master.so.1
%attr(0755, root, root) %{_libdir}/libpostfix-util.so.1
%attr(0755, root, root) %{_libdir}/libpostfix-tls.so.1
%attr(0755, root, root) %{_libdir}/libpostfix-milter.so.1
%attr(0755, root, root) %{_libdir}/libpostfix-xsasl.so.1


%post -n %{libname} -p /sbin/ldconfig
%postun -n %{libname} -p /sbin/ldconfig

%if %{with ldap}
%files ldap
%attr(755, root, root) %{_libdir}/postfix/dict_ldap.so
%post ldap
%dynmap_add_cmd ldap
%postun ldap
%dynmap_rm_cmd ldap
%endif

%if %{with mysql}
%files mysql
%attr(755, root, root) %{_libdir}/postfix/dict_mysql.so 
%post mysql
%dynmap_add_cmd mysql
%postun mysql
%dynmap_rm_cmd mysql
%endif

%if %{with pam}
%files pam
%attr(755, root, root) %{_libdir}/postfix/dict_pam.so
%post pam
%dynmap_add_cmd pam
%postun pam
%dynmap_rm_cmd pam
%endif

%if %{with pcre}
%files pcre
%attr(755, root, root) %{_libdir}/postfix/dict_pcre.so
%post pcre
%dynmap_add_cmd pcre
%postun pcre
%dynmap_rm_cmd pcre
%endif

%if %{with pgsql}
%files pgsql
%attr(755, root, root) %{_libdir}/postfix/dict_pgsql.so
%post pgsql
%dynmap_add_cmd pgsql
%postun pgsql
%dynmap_rm_cmd pgsql
%endif
%endif

