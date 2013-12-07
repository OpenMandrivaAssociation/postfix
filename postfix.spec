%define _disable_ld_no_undefined 1
%define major 1
%define	libdns %mklibname %{name}-dns %{major}
%define	libglobal %mklibname %{name}-global %{major}
%define	libmaster %mklibname %{name}-master %{major}
%define	libutil %mklibname %{name}-util %{major}
%define	libtls %mklibname %{name}-tls %{major}
%define	libmilter %mklibname %{name}-milter %{major}
%define	libxsasl %mklibname %{name}-xsasl %{major}
%define sendmail_command %{_sbindir}/sendmail.postfix

%define post_install_parameters	daemon_directory=%{_libdir}/postfix command_directory=%{_sbindir} queue_directory=%{queue_directory} sendmail_path=%{sendmail_command} newaliases_path=%{_bindir}/newaliases mailq_path=%{_bindir}/mailq mail_owner=postfix setgid_group=%{maildrop_group} manpage_directory=%{_mandir} readme_directory=%{_docdir}/%{name}/README_FILES html_directory=%{_docdir}/%{name}/html data_directory=/var/lib/postfix

# use bcond_with if default is disabled
# use bcond_without if default is enabled
# built
%bcond_without ldap
%bcond_without mysql
%bcond_without pgsql
%bcond_without sqlite
%bcond_without pcre
%bcond_without sasl
%bcond_without tls
%bcond_without ipv6
%bcond_without cdb
%bcond_without chroot

# Postfix requires one exlusive uid/gid and a 2nd exclusive gid for its own use.
%define maildrop_group	postdrop
%define queue_directory	%{_var}/spool/postfix

# Macro: %{dynmap_add_cmd <name> [<soname>] [-m]}
%define dynmap_add_cmd(m) FILE=%{_sysconfdir}/postfix/dynamicmaps.cf; if ! grep -q "^%{1}[[:space:]]" ${FILE}; then echo "%{1}	%{_libdir}/postfix/dict_%{?2:%{2}}%{?!2:%{1}}.so	dict_%{1}_open%{-m:	mkmap_%{1}_open}" >> ${FILE}; fi;
%define dynmap_rm_cmd() FILE=%{_sysconfdir}/postfix/dynamicmaps.cf; if [ $1 = 0 -a -s $FILE ]; then  cp -p ${FILE} ${FILE}.$$; grep -v "^%{1}[[:space:]]" ${FILE}.$$ > ${FILE}; rm -f ${FILE}.$$; fi;

Summary:	Postfix Mail Transport Agent
Name:		postfix
Epoch:		1
Version:	2.10.2
Release:	3
License:	IBM Public License
Group:		System/Servers
Url:		http://www.postfix.org/
Source0:	ftp://ftp.porcupine.org/mirrors/postfix-release/official/%{name}-%{version}.tar.gz
Source1:	ftp://ftp.porcupine.org/mirrors/postfix-release/official/%{name}-%{version}.tar.gz.sig
Source2:	postfix-main.cf
Source3:	postfix-etc-init.d-postfix
Source4:	postfix-etc-pam.d-smtp
Source5:	postfix-aliases
Source6:	postfix-ip-up
Source7:	postfix-ip-down
Source8:	postfix-ifup-d
Source10:	postfix-README.MDK
Source11:	postfix-README.MDK.update
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
Patch0:		postfix-2.9.1-dynamicmaps.diff
Patch5:		postfix-2.9.1-dynamicmaps2.diff

Patch1:		postfix-2.9.1-mdkconfig.diff
Patch2:		postfix-alternatives-mdk.patch

# dbupgrade patch patch split from dynamicmaps one
Patch3:		postfix-2.9.1-dbupgrade.diff

# sdbm patch patch split from dynamicmaps one
Patch4:		postfix-2.7.0-sdbm.patch

# Shamelessy stolen from debian
Patch6:		postfix-2.2.4-smtpstone.patch

# systemd integration
Source100:	postfix.service

BuildRequires:	db-devel
BuildRequires:	gawk
BuildRequires:	html2text
BuildRequires:	perl-base
BuildRequires:	sed
BuildRequires:	pkgconfig(libtirpc)
%if %{with sasl}
BuildRequires:	sasl-devel >= 2.0
%endif
%if %{with tls}
BuildRequires:	pkgconfig(openssl)
%endif

Provides:	mail-server
Provides:	sendmail-command
# syslog-ng before this version needed a different chroot script, 
# which was bug-prone
Conflicts:	syslog-ng < 3.1-0.beta2.2
# http://archives.mandrivalinux.com/cooker/2005-06/msg01987.php
Requires(post):	chkconfig
Requires:	initscripts
Requires:	syslog-daemon
Requires:	coreutils
Requires:	diffutils
Requires:	gawk
Requires(pre,post,postun,preun):	rpm-helper >= 0.3
Requires(pre,post):	sed
%if %{with tls}
Requires(post):	openssl
%endif
Requires(post,preun):	update-alternatives
Requires(pre):	%{name}-config
Requires:	%{name}-config >= 2.9.0-1

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

PLEASE READ THE %{_defaultdocdir}/%{name}/README.MDK FILE.

%package -n %{libdns}
Summary:	Shared library required to run Postfix
Group:		System/Servers
Obsoletes:	%{_lib}postfix1< 1:2.10.2-2

%description -n %{libdns}
This package contains a shared library used by Postfix.

%package -n %{libglobal}
Summary:	Shared library required to run Postfix
Group:		System/Servers
Conflicts:	%{_lib}postfix1< 1:2.10.2-2

%description -n %{libglobal}
This package contains a shared library used by Postfix.

%package -n %{libmaster}
Summary:	Shared library required to run Postfix
Group:		System/Servers
Conflicts:	%{_lib}postfix1< 1:2.10.2-2

%description -n %{libmaster}
This package contains a shared library used by Postfix.

%package -n %{libutil}
Summary:	Shared library required to run Postfix
Group:		System/Servers
Conflicts:	%{_lib}postfix1< 1:2.10.2-2

%description -n %{libutil}
This package contains a shared library used by Postfix.

%package -n %{libtls}
Summary:	Shared library required to run Postfix
Group:		System/Servers
Conflicts:	%{_lib}postfix1< 1:2.10.2-2

%description -n %{libtls}
This package contains a shared library used by Postfix.

%package -n %{libmilter}
Summary:	Shared library required to run Postfix
Group:		System/Servers
Conflicts:	%{_lib}postfix1< 1:2.10.2-2

%description -n %{libmilter}
This package contains a shared library used by Postfix.

%package -n %{libxsasl}
Summary:	Shared library required to run Postfix
Group:		System/Servers
Conflicts:	%{_lib}postfix1< 1:2.10.2-2

%description -n %{libxsasl}
This package contains a shared library used by Postfix.

%if %{with ldap}
%package ldap
Summary:	LDAP map support for Postfix
Group:		System/Servers
BuildRequires:	openldap-devel >= 2.1
Requires:	%{name} = %{EVRD}

%description ldap
This package provides support for LDAP maps in Postfix.
%endif

%if %{with pcre}
%package pcre
Summary:	PCRE map support for Postfix
Group:		System/Servers
BuildRequires:	pkgconfig(libpcre)
Requires:	%{name} = %{EVRD}

%description pcre
This package provides support for PCRE (perl compatible regular expression)
maps in Postfix.
%endif

%if %{with mysql}
%package mysql
Summary:	MYSQL map support for Postfix
Group:		System/Servers
BuildRequires:	mysql-devel
Requires:	%{name} = %{EVRD}

%description mysql
This package provides support for MYSQL maps in Postfix.
%endif

%if %{with pgsql}
%package pgsql
Summary:	Postgres SQL map support for Postfix
Group:		System/Servers
BuildRequires:	postgresql-devel
Requires:	%{name} = %{EVRD}

%description pgsql
This package provides support for Postgres SQL maps in Postfix.
%endif

%if %{with sqlite}
%package sqlite
Summary:	SQLite map support for Postfix
Group:		System/Servers
BuildRequires:	pkgconfig(sqlite3)
Requires:	%{name} = %{EVRD}

%description sqlite
This package provides support for SQLite maps in Postfix.
%endif

%if %{with cdb}
%package cdb
Summary:	CDB map support for Postfix
Group:		System/Servers
BuildRequires:	pkgconfig(libcdb)
Requires:	%{name} = %{EVRD}

%description cdb
This package provides support for CDB maps in Postfix.
%endif

%package config-standalone
Summary:	Default configuration files for running Postfix standalone
Provides:	%{name}-config = %{version}-%{release}
Conflicts:	%{name}-config-dovecot

%description config-standalone
Default configuration files for running Postfix standalone.

Use this config if you intend to run Postfix without dovecot.
Alternatively, install %{name}-config-dovecot for the
postfix/dovecot combo.

%prep
%setup -q
%apply_patches
# no backup files here, otherwise they get included in %%doc
find . -name \*.orig -exec rm {} \;

mkdir -p conf/dist
mv conf/main.cf conf/dist
cp %{SOURCE2} conf/main.cf

# ugly hack for 32/64 arches
if [ %{_lib} != lib ]; then
	sed -i -e 's@^/usr/lib/@%{_libdir}/@' conf/postfix-files
	sed -i -e "s@/lib/@/%{_lib}/@g" conf/main.cf
fi

install -m644 %{SOURCE10} README.MDK
install -m644 %{SOURCE11} README.MDK.update
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
# it does not work with -fPIE and someone added that to the serverbuild macro...
CFLAGS=`echo $CFLAGS|sed -e 's|-fPIE||g'`
CXXFLAGS=`echo $CXXFLAGS|sed -e 's|-fPIE||g'`
RPM_OPT_FLAGS=`echo $RPM_OPT_FLAGS|sed -e 's|-fPIE||g'`

OPT="$RPM_OPT_FLAGS"
DEBUG=
CCARGS=
AUXLIBS="%{?ldflags:%ldflags}"
AUXLIBS=`echo $AUXLIBS|sed -e 's|-fPIE||g'`

# the patch is mixed with SDBM support :(
  CCARGS="${CCARGS} -DHAS_SDBM -DHAS_DLOPEN"

%if %{with ldap}
  CCARGS="${CCARGS} -DHAS_LDAP"
%endif
%if %{with pcre}
  CCARGS="${CCARGS} -DHAS_PCRE"
%endif
%if %{with mysql}
  CCARGS="${CCARGS} -DHAS_MYSQL -I/usr/include/mysql"
%endif
%if %{with pgsql}
  CCARGS="${CCARGS} -DHAS_PGSQL -I/usr/include/pgsql"
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
%endif

export CCARGS AUXLIBS OPT DEBUG
make -f Makefile.init makefiles

unset CCARGS AUXLIBS DEBUG OPT
make
make manpages

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

# add correct parameters to main.cf.dist
LD_LIBRARY_PATH=$PWD/lib${LD_LIBRARY_PATH:+:}${LD_LIBRARY_PATH} \
	./src/postconf/postconf -c ./conf/dist -e \
	%post_install_parameters
mv conf/dist/main.cf conf/main.cf.dist

%install
# install postfix into the build root
LD_LIBRARY_PATH=$PWD/lib${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH} \
make non-interactive-package \
	install_root=%{buildroot} \
	config_directory=%{_sysconfdir}/postfix \
	%post_install_parameters \
	|| exit 1

mkdir -p %{buildroot}/var/lib/postfix

for i in lib/*.a; do
	j=${i#lib/lib}
	install $i %{buildroot}%{_libdir}/libpostfix-${j%.a}.so.1
done

# rpm %%doc macro wants to take his files in buildroot
rm -fr DOC
mkdir DOC
mv %{buildroot}%{_docdir}/%{name}/html DOC/html
mv %{buildroot}%{_docdir}/%{name}/README_FILES DOC/README_FILES

# for sasl configuration
mkdir -p %{buildroot}%{_sysconfdir}/sasl2
cp %{SOURCE15} %{buildroot}%{_sysconfdir}/sasl2/smtpd.conf

mkdir -p %{buildroot}%{_sysconfdir}/pam.d
install -c %{SOURCE4} %{buildroot}%{_sysconfdir}/pam.d/smtp

mkdir -p %{buildroot}%{_sysconfdir}/ppp/ip-{up,down}.d
install -c %{SOURCE6} %{buildroot}%{_sysconfdir}/ppp/ip-up.d/postfix
install -c %{SOURCE7} %{buildroot}%{_sysconfdir}/ppp/ip-down.d/postfix

mkdir -p %{buildroot}%{_sysconfdir}/resolvconf/update-libc.d/
install -c %{SOURCE8} %{buildroot}%{_sysconfdir}/resolvconf/update-libc.d/postfix

mkdir -p %{buildroot}%{_sysconfdir}/sysconfig
touch %{buildroot}%{_sysconfdir}/sysconfig/postfix

# this is used by some examples (cyrus)
mkdir -p %{buildroot}%{queue_directory}/extern

install -c auxiliary/rmail/rmail %{buildroot}%{_bindir}/rmail

# copy new aliases files and generate a ghost aliases.db file
cp -f %{SOURCE5} %{buildroot}%{_sysconfdir}/postfix/aliases
chmod 644 %{buildroot}%{_sysconfdir}/postfix/aliases
touch %{buildroot}%{_sysconfdir}/postfix/aliases.db

# install chroot script and postfinger
install -m 0755 %{SOURCE14} %{buildroot}%{_sbindir}/postfix-chroot.sh
install -m 0755 %{SOURCE21} %{buildroot}%{_sbindir}/postfinger

# install qshape
install -m755 auxiliary/qshape/qshape.pl %{buildroot}%{_sbindir}/qshape
cp man/man1/qshape.1 %{buildroot}%{_mandir}/man1/qshape.1

# systemd
mkdir -p %buildroot/lib/systemd/system
install -c -m 644 %SOURCE100 %buildroot/lib/systemd/system/

# RPM compresses man pages automatically.
# - Edit postfix-files to reflect this, so post-install won't get confused
#   when called during package installation.
sed -i -e "s@\(/man[158]/.*\.[158]\):@\1%{_extension}:@" %{buildroot}%{_libdir}/postfix/postfix-files

# remove files that are not in the main package
sed -i -e "/dict_.*\.so/d" %{buildroot}%{_libdir}/postfix/postfix-files

# remove sample_directory from main.cf (#15297)
# the default is /etc/postfix
sed -i -e "/^sample_directory/d" %{buildroot}%{_sysconfdir}/postfix/main.cf

%pre
%_pre_useradd postfix %{queue_directory} /bin/false
%_pre_groupadd %{maildrop_group} postfix
# disable chroot of spawn service in /etc/sysconfig/postfix, 
# but do it only once and only if user did not
# modify /etc/sysconfig/postfix manually
if grep -qs "^NEVER_CHROOT_PROGRAM='^(proxymap|local|pipe|virtual)$'$" /etc/sysconfig/postfix; then
	if ! grep -qs "^NEVER_CHROOT_PROGRAM='^(proxymap|local|pipe|virtual|spawn)$'$" /usr/sbin/postfix-chroot.sh; then
		perl -pi -e "s/^NEVER_CHROOT_PROGRAM=.*\$/NEVER_CHROOT_PROGRAM=\'^(proxymap|local|pipe|virtual|spawn)\\\$\'/" /etc/sysconfig/postfix
	fi
fi
# disable some unneeded and potentially harmful nss libraries in 
# /etc/sysconfig/postfix, but do it only once and only if user did not
# modify /etc/sysconfig/postfix manually
if grep -qs "^IGNORE_NSS_LIBS='^$'$" /etc/sysconfig/postfix; then
	if ! grep -qs "^IGNORE_NSS_LIBS='^(mdns.*|ldap|db|wins)$'$" /usr/sbin/postfix-chroot.sh; then
		perl -pi -e "s/^IGNORE_NSS_LIBS=.*\$/IGNORE_NSS_LIBS=\'^(mdns.*|ldap|db|wins)\\\$\'/" /etc/sysconfig/postfix
	fi
fi

%post
%systemd_post %{name}.service

# we don't have these maps anymore as separate packages/plugins:
# cidr, tcp and sdbm (2007.0)
if [ "$1" -eq "2" ]; then
	sed -i "/^cidr/d;/^sdbm/d;/^tcp/d" %{_sysconfdir}/postfix/dynamicmaps.cf
fi

# upgrade configuration files if necessary
%{_sbindir}/postfix \
	set-permissions \
	upgrade-configuration \
	config_directory=%{_sysconfdir}/postfix \
	%post_install_parameters

# move previous sasl configuration files to new location if applicable
# have to go through many loops to prevent damaging user configuration
# this changed around 2007.0 so it should go away soon
saslpath=`postconf -h smtpd_sasl_path`
if [ "${saslpath}" != "${saslpath##*:}" -o "${saslpath}" != "${saslpath##*/usr/lib}" ]; then
	postconf -e smtpd_sasl_path=smtpd
fi

for old_smtpd_conf in /etc/postfix/sasl/smtpd.conf %{_libdir}/sasl2/smtpd.conf; do
	if [ -e ${old_smtpd_conf} ]; then
		if ! grep -qsve '^\(#.*\|[[:space:]]*\)$' /etc/sasl2/smtpd.conf; then
			# /etc/sasl2/smtpd.conf missing or just comments
			if [ -s /etc/sasl2/smtpd.conf ] && [ ! -e /etc/sasl2/smtpd.conf.rpmnew -o /etc/sasl2/smtpd.conf -nt /etc/sasl2/smtpd.conf.rpmnew ]; then
				mv /etc/sasl2/smtpd.conf /etc/sasl2/smtpd.conf.rpmnew
			fi
			mv ${old_smtpd_conf} /etc/sasl2/smtpd.conf
		else
			echo "warning: existing ${old_smtpd_conf} will be ignored"
		fi
	fi
done

%if %{with tls}
%_create_ssl_certificate postfix
%endif

if [ -e /etc/sysconfig/postfix ]; then
	%{_sbindir}/postfix-chroot.sh -q update
else
%if %{with chroot}
	%{_sbindir}/postfix-chroot.sh -q enable
%else
	%{_sbindir}/postfix-chroot.sh -q create_sysconfig
%endif
fi
%_post_service postfix

/usr/sbin/update-alternatives --install %{_sbindir}/sendmail sendmail-command %{sendmail_command} 30 --slave %{_prefix}/lib/sendmail sendmail-command-in_libdir %{sendmail_command}

%triggerin -- glibc setup nss_ldap nss_db nss_wins nss_mdns
# Generate chroot jails on the fly when needed things are installed/upgraded
%{_sbindir}/postfix-chroot.sh -q update

%preun
%systemd_preun %{name}.service

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
	# Clean up chroot environment and spool directory
	%{_sbindir}/postfix-chroot.sh -q remove
	cd %{queue_directory} && queue_directory_remove || true
fi

%postun
%_postun_userdel postfix
%_postun_groupdel %{maildrop_group}
if [ ! -e %{sendmail_command} ]; then
	/usr/sbin/update-alternatives --remove sendmail-command %{sendmail_command} 
fi
%_systemd_postun_with_restart %{name}.service

%files
%dir %{_sysconfdir}/postfix
%config(noreplace) %{_sysconfdir}/sasl2/smtpd.conf
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
%config(noreplace) %{_sysconfdir}/postfix/dynamicmaps.cf
%attr(0644, root, root) /lib/systemd/system/%{name}.service
%attr(0644, root, root) %config(noreplace) %{_sysconfdir}/pam.d/smtp
%attr(0755, root, root) %config(noreplace) %{_sysconfdir}/ppp/ip-up.d/postfix
%attr(0755, root, root) %config(noreplace) %{_sysconfdir}/ppp/ip-down.d/postfix
%attr(0755, root, root) %config(noreplace) %{_sysconfdir}/resolvconf/update-libc.d/postfix
%ghost %{_sysconfdir}/sysconfig/postfix

%dir %attr(0700, postfix, root) /var/lib/postfix

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
%attr(0644, root, root) %{_libdir}/postfix/postfix-files
%attr(0755, root, root) %{_libdir}/postfix/anvil
%attr(0755, root, root) %{_libdir}/postfix/bounce
%attr(0755, root, root) %{_libdir}/postfix/cleanup
%attr(0755, root, root) %{_libdir}/postfix/discard
%attr(0755, root, root) %{_libdir}/postfix/dnsblog
%attr(0755, root, root) %{_libdir}/postfix/error
%attr(0755, root, root) %{_libdir}/postfix/flush
%attr(0755, root, root) %{_libdir}/postfix/lmtp
%attr(0755, root, root) %{_libdir}/postfix/local
%attr(0755, root, root) %{_libdir}/postfix/master
%attr(0755, root, root) %{_libdir}/postfix/nqmgr
%attr(0755, root, root) %{_libdir}/postfix/oqmgr
%attr(0755, root, root) %{_libdir}/postfix/pickup
%attr(0755, root, root) %{_libdir}/postfix/pipe
%attr(0755, root, root) %{_libdir}/postfix/postfix-script
%attr(0755, root, root) %{_libdir}/postfix/postfix-wrapper
%attr(0755, root, root) %{_libdir}/postfix/post-install
%attr(0755, root, root) %{_libdir}/postfix/postmulti-script
%attr(0755, root, root) %{_libdir}/postfix/postscreen
%attr(0755, root, root) %{_libdir}/postfix/proxymap
%attr(0755, root, root) %{_libdir}/postfix/qmgr
%attr(0755, root, root) %{_libdir}/postfix/qmqpd
%attr(0755, root, root) %{_libdir}/postfix/scache
%attr(0755, root, root) %{_libdir}/postfix/showq
%attr(0755, root, root) %{_libdir}/postfix/smtp
%attr(0755, root, root) %{_libdir}/postfix/smtpd
%attr(0755, root, root) %{_libdir}/postfix/spawn
%attr(0755, root, root) %{_libdir}/postfix/tlsmgr
%attr(0755, root, root) %{_libdir}/postfix/tlsproxy
%attr(0755, root, root) %{_libdir}/postfix/trivial-rewrite
%attr(0755, root, root) %{_libdir}/postfix/verify
%attr(0755, root, root) %{_libdir}/postfix/virtual

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
%attr(0755, root, root) %{_sbindir}/postmulti
%attr(0755, root, root) %{_sbindir}/postsuper
%attr(0755, root, root) %{_sbindir}/qmqp-sink
%attr(0755, root, root) %{_sbindir}/qmqp-source
%attr(0755, root, root) %{_sbindir}/smtp-sink
%attr(0755, root, root) %{_sbindir}/smtp-source
%attr(0755, root, root) %{_sbindir}/postfinger
%attr(0755, root, root) %{_sbindir}/postfix-chroot.sh
%attr(0755, root, root) %{_sbindir}/qshape
%attr(0755, root, root) %{sendmail_command}
%attr(0755, root, root) %{_bindir}/mailq
%attr(0755, root, root) %{_bindir}/newaliases
%attr(0755, root, root) %{_bindir}/rmail
%{_mandir}/man1/*
%{_mandir}/man5/*
%{_mandir}/man8/*

%files -n %{libdns}
%{_libdir}/libpostfix-dns.so.%{major}

%files -n %{libglobal}
%{_libdir}/libpostfix-global.so.%{major}

%files -n %{libmaster}
%{_libdir}/libpostfix-master.so.%{major}

%files -n %{libutil}
%{_libdir}/libpostfix-util.so.%{major}

%files -n %{libtls}
%{_libdir}/libpostfix-tls.so.%{major}

%files -n %{libmilter}
%{_libdir}/libpostfix-milter.so.%{major}

%files -n %{libxsasl}
%{_libdir}/libpostfix-xsasl.so.%{major}

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

%if %{with sqlite}
%files sqlite
%attr(755, root, root) %{_libdir}/postfix/dict_sqlite.so

%post sqlite
%dynmap_add_cmd sqlite
%postun sqlite
%dynmap_rm_cmd sqlite
%endif

%if %{with cdb}
%files cdb
%attr(755, root, root) %{_libdir}/postfix/dict_cdb.so

%post cdb
%dynmap_add_cmd cdb -m
%postun cdb
%dynmap_rm_cmd cdb
%endif

%files config-standalone
%config(noreplace) %{_sysconfdir}/postfix/main.cf
# http://archives.mandrivalinux.com/cooker/2005-07/msg01109.php
%{_sysconfdir}/postfix/main.cf.dist
%{_sysconfdir}/postfix/main.cf.default
%{_sysconfdir}/postfix/bounce.cf.default
%config(noreplace) %{_sysconfdir}/postfix/master.cf
%attr(0644, root, root) %{_libdir}/postfix/main.cf
%attr(0644, root, root) %{_libdir}/postfix/master.cf

