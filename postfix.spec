%define _disable_ld_no_undefined 1
%define major %{nil}
%define sendmail_command %{_sbindir}/sendmail.postfix

# use bcond_with if default is disabled
# use bcond_without if default is enabled
# built
%bcond_without ldap
%bcond_without mysql
%bcond_without pgsql
%bcond_without sdbm
%bcond_without sqlite
%bcond_without pcre
%bcond_without sasl
%bcond_without tls
%bcond_without ipv6
%bcond_without cdb

# Postfix requires one exlusive uid/gid and a 2nd exclusive gid for its own use.
%define maildrop_group	postdrop
%define queue_directory	%{_var}/spool/postfix
%define postfix_shlib_dir %{_libdir}/postfix

%define post_install_parameters	daemon_directory=%{_libexecdir}/postfix command_directory=%{_sbindir} queue_directory=%{queue_directory} sendmail_path=%{sendmail_command} newaliases_path=%{_bindir}/newaliases mailq_path=%{_bindir}/mailq mail_owner=postfix setgid_group=%{maildrop_group} manpage_directory=%{_mandir} readme_directory=%{_docdir}/%{name}/README_FILES html_directory=%{_docdir}/%{name}/html data_directory=/var/lib/postfix shlib_directory=%{postfix_shlib_dir}

Summary:	Postfix Mail Transport Agent
Name:		postfix
Version:	3.11.0
Release:	2
License:	IBM Public License
Group:		System/Servers
Url:		https://www.postfix.org/
Source0:	ftp://ftp.porcupine.org/mirrors/postfix-release/official/%{name}-%{version}.tar.gz
Source1:	ftp://ftp.porcupine.org/mirrors/postfix-release/official/%{name}-%{version}.tar.gz.sig
Source2:	postfix-main.cf
Source4:	postfix-etc-pam.d-smtp
Source5:	postfix-aliases
Source6:	postfix-ip-up
Source7:	postfix-ip-down
Source8:	postfix-ifup-d
Source10:	postfix-README.MDK
Source11:	postfix-README.MDK.update
Source12:	postfix-bash-completion
Source13:	http://www.seaglass.com/postfix/faq.html
Source15:	postfix-smtpd.conf

# Jim Seymour stuff
Source25:	http://jimsun.LinxNet.com/misc/postfix-anti-UCE.txt
Source26:	http://jimsun.LinxNet.com/misc/header_checks.txt
Source27:	http://jimsun.LinxNet.com/misc/body_checks.txt

Patch1:		postfix-2.9.1-mdkconfig.diff
Patch2:		postfix-alternatives-mdk.patch
Patch3:		postfix-3.6.3-glibc-2.34.patch

# sdbm patch patch split from dynamicmaps one
Patch4:		postfix-2.7.0-sdbm.patch

# Don't warn about symlinks being group- or other-writable
# (they always are)
Patch5:		postfix-3.1.2-dont-warn-about-symlinks.patch

# Shamelessy stolen from debian
Patch6:		postfix-2.2.4-smtpstone.patch

# Teach postfix about dovecot delivery
# (in most cases, using lmtp is preferable though...)
Patch7:		postfix-3.1.2-dovecot-delivery.patch

Patch8:		postfix-3.2.4-lib-interdependencies.patch

# systemd integration
Source100:	postfix.service
Source101:	postfix.aliasesdb

BuildRequires:	make
BuildRequires:	m4
BuildRequires:	db-devel >= 18
BuildRequires:	gawk
BuildRequires:	html2text
BuildRequires:	perl-base
BuildRequires:	sed
BuildRequires:	pkgconfig(libtirpc)
BuildRequires:	pkgconfig(icu-uc)
BuildRequires:	pkgconfig(lmdb)
# For col (used by the doc build process)
BuildRequires:	util-linux
# For _create_ssl_certificate macro
BuildRequires:	rpm-helper
%if %{with sasl}
BuildRequires:	sasl-devel >= 2.0
%endif
%if %{with tls}
BuildRequires:	pkgconfig(openssl)
%endif

Provides:	mail-server
Provides:	sendmail-command
# http://archives.mandrivalinux.com/cooker/2005-06/msg01987.php
Requires(post):	chkconfig
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

# Before 2026-02-26, pf 3.10.8-2, after 6.0, we split those internal
# libraries into separate packages.
# We no longer do this (the libraries are useless on their
# own and they're all required by the core postfix binary).
# FIXME Get rid of the obsoletion once we're reasonably sure all
# previous users of the package have updated.
%define	libdns %mklibname %{name}-dns %{major}
%define	libglobal %mklibname %{name}-global %{major}
%define	libmaster %mklibname %{name}-master %{major}
%define	libutil %mklibname %{name}-util %{major}
%define	libtls %mklibname %{name}-tls %{major}
Obsoletes:	%{libdns} < %{EVRD}
Obsoletes:	%{libglobal} < %{EVRD}
Obsoletes:	%{libmaster} < %{EVRD}
Obsoletes:	%{libutil} < %{EVRD}
Obsoletes:	%{libtls} < %{EVRD}

%description
Postfix is a Mail Transport Agent (MTA), supporting LDAP, SMTP AUTH (SASL),
TLS and running in a hardened environment.

Postfix is Wietse Venema's mailer that started life as an alternative
to the widely-used Sendmail program.
Postfix attempts to be fast, easy to administer, and secure, while at
the same time being sendmail compatible enough to not upset existing
users. Thus, the outside has a sendmail-ish flavor, but the inside is
completely different.
This software was formerly known as VMailer. It was released by the end
of 1998 as the IBM Secure Mailer. From then on it has lived on as Postfix.

PLEASE READ THE %{_defaultdocdir}/%{name}/README.MDK FILE.

%if %{with ldap}
%package ldap
Summary:	LDAP map support for Postfix
Group:		System/Servers
BuildRequires:	pkgconfig(ldap)
Requires:	%{name} = %{EVRD}

%description ldap
This package provides support for LDAP maps in Postfix.
%endif

%if %{with pcre}
%package pcre
Summary:	PCRE map support for Postfix
Group:		System/Servers
BuildRequires:	pkgconfig(libpcre2-8)
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

%if %{with sdbm}
%package sdbm
Summary:	SDBM map support for Postfix
Group:		System/Servers
Requires:	%{name} = %{EVRD}

%description sdbm
This package provides support for SDBM maps in Postfix.
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
%autopatch -p1
# no backup files here, otherwise they get included in %%doc
find . -name \*.orig -exec rm {} \;

mkdir -p conf/dist
mv conf/main.cf conf/dist
cp %{SOURCE2} conf/main.cf

# Change DEF_SHLIB_DIR according to build host
sed -i \
's|^\(\s*#define\s\+DEF_SHLIB_DIR\s\+\)"/usr/lib/postfix"|\1"%{_libdir}/postfix"|' \
src/global/mail_params.h
%if "%{_mandir}" != "/usr/local/man"
sed -i -e 's,/usr/local/man,%{_mandir},g' src/global/mail_params.h
%endif

# Default to the latest and greatest COMPATIBILITY_LEVEL, not the oldest possible
sed -i -e 's/^#define DEF_COMPAT_LEVEL[[:space:]].*/#define DEF_COMPAT_LEVEL LAST_COMPAT_LEVEL/' src/global/mail_params.h

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

# use sed to fix mantools/postlink for our non posix sed
#cp -p mantools/postlink mantools/postlink.posix
#sed -e 's/\[\[:<:\]\]/\\</g; s/\[\[:>:\]\]/\\>/g' mantools/postlink.posix > mantools/postlink
# XXX - andreas - original postlink with perl is segfaulting
cp -p mantools/postlink.sed mantools/postlink.posix
sed -e 's/\[\[:<:\]\]/\\</g; s/\[\[:>:\]\]/\\>/g' mantools/postlink.posix > mantools/postlink

%build
%serverbuild_hardened
# it does not work with -fPIE and someone added that to the serverbuild macro...
CFLAGS=`echo $CFLAGS|sed -e 's|-fPIE||g'`
CXXFLAGS=`echo $CXXFLAGS|sed -e 's|-fPIE||g'`
RPM_OPT_FLAGS=`echo $RPM_OPT_FLAGS|sed -e 's|-fPIE||g'`

OPT="$RPM_OPT_FLAGS"
DEBUG=
CCARGS="-DNO_NIS -DNO_NETINFO -DHAS_EAI -DHAS_DLOPEN"
AUXLIBS="%{?ldflags:%ldflags}"
AUXLIBS=`echo $AUXLIBS|sed -e 's|-fPIE||g'`

# LMDB is mandatory because it's the default for aliases etc. now
CCARGS="${CCARGS} -DHAS_LMDB -DDEF_DB_TYPE=\\\"lmdb\\\" -DDEF_CACHE_DB_TYPE=\\\"lmdb\\\""
AUXLIBS_LMDB="$(pkg-config --libs lmdb)"

%if %{with ldap}
  CCARGS="${CCARGS} -DHAS_LDAP"
  AUXLIBS_LDAP="-lldap -llber"
%endif
%if %{with pcre}
  CCARGS="${CCARGS} -DHAS_PCRE=2 `pcre2-config --cflags`"
  AUXLIBS_PCRE="$(pcre2-config --libs8)"
%endif
%if %{with sqlite}
  CCARGS="${CCARGS} -DHAS_SQLITE `pkg-config --cflags sqlite3`"
  AUXLIBS_SQLITE="`pkg-config --libs sqlite3`"
%endif
%if %{with mysql}
  CCARGS="${CCARGS} -DHAS_MYSQL -I/usr/include/mysql"
  AUXLIBS_MYSQL="$(pkg-config --libs mariadb)"
%endif
%if %{with pgsql}
  CCARGS="${CCARGS} -DHAS_PGSQL -I/usr/include/pgsql"
  AUXLIBS_PGSQL="$(pkg-config --libs libpq)"
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
%if %{with sdbm}
  CCARGS="${CCARGS} -DHAS_SDBM"
%endif

export CCARGS AUXLIBS AUXLIBS_PCRE AUXLIBS_LDAP AUXLIBS_LMDB AUXLIBS_MYSQL AUXLIBS_PGSQL AUXLIBS_SQLITE OPT DEBUG
export CC="%{__cc}"
export CXX="%{__cxx}"
make -f Makefile.init makefiles dynamicmaps=yes pie=yes \
	shlib_directory="%{postfix_shlib_dir}" \
	%{post_install_parameters} \
	SHLIB_RPATH="-Wl,-rpath,%{postfix_shlib_dir} %{ldflags}" \
	OPT="$RPM_OPT_FLAGS -fno-strict-aliasing -Wno-comment" \
	POSTFIX_INSTALL_OPTS=-keep-build-mtime

unset CCARGS AUXLIBS DEBUG OPT
make
make manpages

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
	shlib_directory=%{postfix_shlib_dir} \
	config_directory=%{_sysconfdir}/postfix \
	%post_install_parameters \
	|| exit 1

mkdir -p %{buildroot}/var/lib/postfix

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

touch %{buildroot}%{_sysconfdir}/postfix/domains

# install qshape
install -m755 auxiliary/qshape/qshape.pl %{buildroot}%{_sbindir}/qshape
cp man/man1/qshape.1 %{buildroot}%{_mandir}/man1/qshape.1

# systemd
mkdir -p %buildroot%{_unitdir}
install -c -m 644 %SOURCE100 %buildroot%{_unitdir}/
install -m 755 %{SOURCE101} %{buildroot}%{_sysconfdir}/postfix/aliasesdb
install -d %{buildroot}%{_presetdir}
cat > %{buildroot}%{_presetdir}/86-postfix.preset << EOF
enable postfix.service
EOF

# remove sample_directory from main.cf (#15297)
# the default is /etc/postfix
sed -i -e "/^sample_directory/d" %{buildroot}%{_sysconfdir}/postfix/main.cf

# users/groups
# WARNING: If you change this here, you also need to change
# it in the %%pre script. We can't use the usual sysusers_create_package
# macro because of the dynamic insertions (maildrop_group/queue_directory)
# at build time.
mkdir -p %{buildroot}%{_sysusersdir}
cat >%{buildroot}%{_sysusersdir}/postfix.conf <<EOF
g %{maildrop_group} 75
u postfix 73 "Postfix mail system" %{queue_directory}
EOF

# Handle the plugin and file registries
mkdir -p %{buildroot}%{_sysconfdir}/postfix/postfix-files.d
rm -f %{buildroot}%{_sysconfdir}/postfix/dynamicmaps.cf
mkdir -p %{buildroot}%{_sysconfdir}/postfix/dynamicmaps.cf.d
for i in cdb ldap lmdb mysql pcre pgsql sdbm sqlite; do
	[ -e %{buildroot}%{_libdir}/postfix/postfix-${i}.so ] || continue
	grep -h postfix-${i}.so %{buildroot}%{_sysconfdir}/postfix/postfix-files >%{buildroot}%{_sysconfdir}/postfix/postfix-files.d/${i}
	sed -i -e "/postfix-${i}\.so/d" %{buildroot}%{_sysconfdir}/postfix/postfix-files
	if nm -D %{buildroot}%{_libdir}/postfix/postfix-${i}.so |grep -q mkmap_${i}_open; then
		MKMAP="	mkmap_${i}_open"
	else
		MKMAP=""
	fi
	echo "${i}	%{_libdir}/postfix/postfix-${i}.so	dict_${i}_open${MKMAP}" >%{buildroot}%{_sysconfdir}/postfix/dynamicmaps.cf.d/${i}.cf
done

# Post-process /etc/postfix/postfix-files some more, postfix can freak
# out badly if a file mentioned there is "missing".
# postfix tries to be super smart and auto-correct values like
# shlib_directories in /etc/postfix/main.cf if it thinks they're wrong.
# It thinks they're wrong if a file that is supposed to be there
# according to /etc/postfix/postfix-files isn't there, and resets to
# a "safe" default -- %{_libdir} -- which is actually wrong.
# Outside of splitting libraries into separate packages (already
# handled above), we also kill dynamicmaps.cf in favor of
# dynamicmaps.cf.d
sed -i -e "/dynamicmaps.cf:/d" %{buildroot}%{_sysconfdir}/postfix/postfix-files
# RPM compresses man pages automatically.
# - Edit postfix-files to reflect this, so post-install won't get confused
#   when called during package installation.
sed -i -e "s@\(/man[158]/.*\.[158]\):@\1%{_extension}:@" %{buildroot}%{_sysconfdir}/postfix/postfix-files



%post
# remove relic from pre-3.11.0 (OM 6.1 2026/03/07) -
# used to be a %%config(noreplace) file, is now replaced
# by /etc/postfix/dynamicmaps.cf.d entries
rm -f %{_sysconfdir}/postfix/dynamicmaps.cf &>/dev/null
rm -f %{_sysconfdir}/postfix/dynamicmaps.cf.rpm* &>/dev/null

#ensure the db files are created
%{_sbindir}/postmap /etc/postfix/virtual
%{_sbindir}/postmap /etc/postfix/domains

# upgrade configuration files if necessary
%{_sbindir}/postfix \
	set-permissions \
	upgrade-configuration \
	config_directory=%{_sysconfdir}/postfix \
	%post_install_parameters

%if %{with tls}
%_create_ssl_certificate postfix
%endif

/usr/sbin/update-alternatives --install %{_sbindir}/sendmail sendmail-command %{sendmail_command} 30 --slave %{_prefix}/lib/sendmail sendmail-command-in_libdir %{sendmail_command}

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

if [ $1 = 0 ]; then
	# Clean up spool directory
	cd %{queue_directory} && queue_directory_remove || true
fi

%postun
if [ ! -e %{sendmail_command} ]; then
	/usr/sbin/update-alternatives --remove sendmail-command %{sendmail_command}
fi

%files
%dir %{_sysconfdir}/postfix
%config(noreplace) %{_sysconfdir}/postfix/access
%config(noreplace) %{_sysconfdir}/postfix/aliases
%ghost %{_sysconfdir}/postfix/aliases.db
%config(noreplace) %{_sysconfdir}/postfix/canonical
%config(noreplace) %{_sysconfdir}/postfix/generic
%config(noreplace) %{_sysconfdir}/postfix/header_checks
%config(noreplace) %{_sysconfdir}/postfix/relocated
%config(noreplace) %{_sysconfdir}/postfix/transport
%config(noreplace) %{_sysconfdir}/postfix/virtual
%config(noreplace) %{_sysconfdir}/postfix/domains
%{_sysconfdir}/postfix/main.cf.default
%{_sysconfdir}/postfix/main.cf.dist
%{_sysconfdir}/postfix/main.cf.proto
%{_sysconfdir}/postfix/bounce.cf.default
%attr(0644, root, root) %{_sysconfdir}/postfix/master.cf.proto
%{_sysusersdir}/postfix.conf
%{_sysconfdir}/postfix/aliasesdb
%{_sysconfdir}/postfix/makedefs.out
%{_presetdir}/86-postfix.preset
%attr(0644, root, root) %{_unitdir}/%{name}.service
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

%dir %{_libexecdir}/postfix
%dir %attr(0755, root, root) %{_sysconfdir}/postfix/postfix-files.d
%attr(0644, root, root) %{_sysconfdir}/postfix/postfix-files
%attr(0755, root, root) %{_libexecdir}/postfix/anvil
%attr(0755, root, root) %{_libexecdir}/postfix/bounce
%attr(0755, root, root) %{_libexecdir}/postfix/cleanup
%attr(0755, root, root) %{_libexecdir}/postfix/discard
%attr(0755, root, root) %{_libexecdir}/postfix/dnsblog
%attr(0755, root, root) %{_libexecdir}/postfix/error
%attr(0755, root, root) %{_libexecdir}/postfix/flush
%attr(0755, root, root) %{_libexecdir}/postfix/lmtp
%attr(0755, root, root) %{_libexecdir}/postfix/local
%attr(0755, root, root) %{_libexecdir}/postfix/master
%attr(0755, root, root) %{_libexecdir}/postfix/nbdb_reindexd
%attr(0755, root, root) %{_libexecdir}/postfix/nqmgr
%attr(0755, root, root) %{_libexecdir}/postfix/oqmgr
%attr(0755, root, root) %{_libexecdir}/postfix/pickup
%attr(0755, root, root) %{_libexecdir}/postfix/pipe
%attr(0755, root, root) %{_libexecdir}/postfix/postfix-script
%attr(0755, root, root) %{_libexecdir}/postfix/postfix-non-bdb-script
%attr(0755, root, root) %{_libexecdir}/postfix/postfix-tls-script
%attr(0755, root, root) %{_libexecdir}/postfix/postfix-wrapper
%attr(0755, root, root) %{_libexecdir}/postfix/postlogd
%attr(0755, root, root) %{_libexecdir}/postfix/post-install
%attr(0755, root, root) %{_libexecdir}/postfix/postmulti-script
%attr(0755, root, root) %{_libexecdir}/postfix/postscreen
%attr(0755, root, root) %{_libexecdir}/postfix/proxymap
%attr(0755, root, root) %{_libexecdir}/postfix/qmgr
%attr(0755, root, root) %{_libexecdir}/postfix/qmqpd
%attr(0755, root, root) %{_libexecdir}/postfix/scache
%attr(0755, root, root) %{_libexecdir}/postfix/showq
%attr(0755, root, root) %{_libexecdir}/postfix/smtp
%attr(0755, root, root) %{_libexecdir}/postfix/smtpd
%attr(0755, root, root) %{_libexecdir}/postfix/spawn
%attr(0755, root, root) %{_libexecdir}/postfix/tlsmgr
%attr(0755, root, root) %{_libexecdir}/postfix/tlsproxy
%attr(0755, root, root) %{_libexecdir}/postfix/trivial-rewrite
%attr(0755, root, root) %{_libexecdir}/postfix/verify
%attr(0755, root, root) %{_libexecdir}/postfix/virtual

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
%attr(0755, root, root) %{_sbindir}/qshape
%attr(0755, root, root) %{sendmail_command}
%{_bindir}/mailq
%{_bindir}/newaliases
%attr(0755, root, root) %{_bindir}/rmail
%{_mandir}/man1/*
%{_mandir}/man5/*
%{_mandir}/man8/*
%{_libdir}/postfix/libpostfix-dns.so
%{_libdir}/postfix/libpostfix-global.so
%attr(755, root, root) %{_libdir}/postfix/postfix-lmdb.so
%{_sysconfdir}/postfix/postfix-files.d/lmdb
%dir %{_sysconfdir}/postfix/dynamicmaps.cf.d
%{_sysconfdir}/postfix/dynamicmaps.cf.d/lmdb.cf
%{_libdir}/postfix/libpostfix-master.so
%{_libdir}/postfix/libpostfix-util.so
%{_libdir}/postfix/libpostfix-tls.so

%if %{with ldap}
%files ldap
%attr(755, root, root) %{_libdir}/postfix/postfix-ldap.so
%{_sysconfdir}/postfix/dynamicmaps.cf.d/ldap.cf
%{_sysconfdir}/postfix/postfix-files.d/ldap
%endif

%if %{with mysql}
%files mysql
%attr(755, root, root) %{_libdir}/postfix/postfix-mysql.so
%{_sysconfdir}/postfix/dynamicmaps.cf.d/mysql.cf
%{_sysconfdir}/postfix/postfix-files.d/mysql
%endif

%if %{with sdbm}
%files sdbm
%attr(755, root, root) %{_libdir}/postfix/postfix-sdbm.so
%{_sysconfdir}/postfix/dynamicmaps.cf.d/sdbm.cf
%{_sysconfdir}/postfix/postfix-files.d/sdbm
%endif

%if %{with pcre}
%files pcre
%attr(755, root, root) %{_libdir}/postfix/postfix-pcre.so
%{_sysconfdir}/postfix/dynamicmaps.cf.d/pcre.cf
%{_sysconfdir}/postfix/postfix-files.d/pcre
%endif

%if %{with pgsql}
%files pgsql
%attr(755, root, root) %{_libdir}/postfix/postfix-pgsql.so
%{_sysconfdir}/postfix/dynamicmaps.cf.d/pgsql.cf
%{_sysconfdir}/postfix/postfix-files.d/pgsql
%endif

%if %{with sqlite}
%files sqlite
%attr(755, root, root) %{_libdir}/postfix/postfix-sqlite.so
%{_sysconfdir}/postfix/dynamicmaps.cf.d/sqlite.cf
%{_sysconfdir}/postfix/postfix-files.d/sqlite
%endif

%if %{with cdb}
%files cdb
%attr(755, root, root) %{_libdir}/postfix/postfix-cdb.so
%{_sysconfdir}/postfix/dynamicmaps.cf.d/cdb.cf
%{_sysconfdir}/postfix/postfix-files.d/cdb
%endif

%files config-standalone
%config(noreplace) %{_sysconfdir}/postfix/main.cf
%config(noreplace) %{_sysconfdir}/postfix/master.cf
%attr(0644, root, root) %config(noreplace) %{_sysconfdir}/pam.d/smtp
%config(noreplace) %{_sysconfdir}/sasl2/smtpd.conf
