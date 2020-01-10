%define _disable_ld_no_undefined 1
%define major %{nil}
%define	libdns %mklibname %{name}-dns %{major}
%define	libglobal %mklibname %{name}-global %{major}
%define	libmaster %mklibname %{name}-master %{major}
%define	libutil %mklibname %{name}-util %{major}
%define	libtls %mklibname %{name}-tls %{major}
### REMOVED in 3.0.0
%define	libmilter %mklibname %{name}-milter 1
### REMOVED in 3.0.0
%define	libxsasl %mklibname %{name}-xsasl 1
%define sendmail_command %{_sbindir}/sendmail.postfix

%define post_install_parameters	daemon_directory=%{_libexecdir}/postfix command_directory=%{_sbindir} queue_directory=%{queue_directory} sendmail_path=%{sendmail_command} newaliases_path=%{_bindir}/newaliases mailq_path=%{_bindir}/mailq mail_owner=postfix setgid_group=%{maildrop_group} manpage_directory=%{_mandir} readme_directory=%{_docdir}/%{name}/README_FILES html_directory=%{_docdir}/%{name}/html data_directory=/var/lib/postfix

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
%bcond_without chroot

# Postfix requires one exlusive uid/gid and a 2nd exclusive gid for its own use.
%define maildrop_group	postdrop
%define queue_directory	%{_var}/spool/postfix
%define postfix_shlib_dir %{_libdir}/postfix

# Macro: %{dynmap_add_cmd <name> [<soname>] [-m]}
%define dynmap_add_cmd(m) FILE=%{_sysconfdir}/postfix/dynamicmaps.cf; if ! grep -q "^%{1}[[:space:]]" ${FILE}; then echo "%{1}	%{_libdir}/postfix/postfix-%{?2:%{2}}%{?!2:%{1}}.so	dict_%{1}_open%{-m:	mkmap_%{1}_open}" >> ${FILE}; fi;
%define dynmap_rm_cmd() FILE=%{_sysconfdir}/postfix/dynamicmaps.cf; if [ $1 = 0 -a -s $FILE ]; then  cp -p ${FILE} ${FILE}.$$; grep -v "^%{1}[[:space:]]" ${FILE}.$$ > ${FILE}; rm -f ${FILE}.$$; fi;

Summary:	Postfix Mail Transport Agent
Name:		postfix
Version:	3.4.8
Release:	1
License:	IBM Public License
Group:		System/Servers
Url:		http://www.postfix.org/
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
Source14:	postfix-chroot.sh
Source15:	postfix-smtpd.conf

# Simon J. Mudd stuff
Source21:	https://ftp.wl0.org/SOURCES/postfinger

# Jim Seymour stuff
Source25:	http://jimsun.LinxNet.com/misc/postfix-anti-UCE.txt
Source26:	http://jimsun.LinxNet.com/misc/header_checks.txt
Source27:	http://jimsun.LinxNet.com/misc/body_checks.txt

Patch1:		postfix-2.9.1-mdkconfig.diff
Patch2:		postfix-alternatives-mdk.patch
Patch3:		postfix-3.4.8-glibc-2.30.patch

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

# Make it build with db > 6.x
Patch9:		postfix-3.3.2-db18.patch

# systemd integration
Source100:	postfix.service
Source101:	postfix.aliasesdb
Source102:	postfix-chroot-update

BuildRequires:	db-devel >= 18
BuildRequires:	gawk
BuildRequires:	html2text
BuildRequires:	perl-base
BuildRequires:	sed
BuildRequires:	pkgconfig(libtirpc)
BuildRequires:	pkgconfig(icu-uc)
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

Obsoletes:	%{libmilter} < %{EVRD}
Obsoletes:	%{libxsasl} < %{EVRD}

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

%description -n %{libdns}
This package contains a shared library used by Postfix.

%package -n %{libglobal}
Summary:	Shared library required to run Postfix
Group:		System/Servers

%description -n %{libglobal}
This package contains a shared library used by Postfix.

%package -n %{libmaster}
Summary:	Shared library required to run Postfix
Group:		System/Servers

%description -n %{libmaster}
This package contains a shared library used by Postfix.

%package -n %{libutil}
Summary:	Shared library required to run Postfix
Group:		System/Servers

%description -n %{libutil}
This package contains a shared library used by Postfix.

%package -n %{libtls}
Summary:	Shared library required to run Postfix
Group:		System/Servers

%description -n %{libtls}
This package contains a shared library used by Postfix.

%package -n %{libmilter}
Summary:	Shared library required to run Postfix
Group:		System/Servers

%description -n %{libmilter}
This package contains a shared library used by Postfix.

%package -n %{libxsasl}
Summary:	Shared library required to run Postfix
Group:		System/Servers

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
%serverbuild_hardened
# it does not work with -fPIE and someone added that to the serverbuild macro...
CFLAGS=`echo $CFLAGS|sed -e 's|-fPIE||g'`
CXXFLAGS=`echo $CXXFLAGS|sed -e 's|-fPIE||g'`
RPM_OPT_FLAGS=`echo $RPM_OPT_FLAGS|sed -e 's|-fPIE||g'`

OPT="$RPM_OPT_FLAGS"
DEBUG=
CCARGS="-DNO_NIS"
AUXLIBS="%{?ldflags:%ldflags}"
AUXLIBS=`echo $AUXLIBS|sed -e 's|-fPIE||g'`

# the patch is mixed with SDBM support :(
  CCARGS="${CCARGS} -DHAS_SDBM -DHAS_DLOPEN"

%if %{with ldap}
  CCARGS="${CCARGS} -DHAS_LDAP"
  AUXLIBS_LDAP="-lldap -llber"
%endif
%if %{with pcre}
  CCARGS="${CCARGS} -DHAS_PCRE"
  AUXLIBS_PCRE="$(pcre-config --libs)"
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

export CCARGS AUXLIBS AUXLIBS_PCRE AUXLIBS_LDAP AUXLIBS_MYSQL AUXLIBS_PGSQL OPT DEBUG
export CC=%{__cc}
export CXX=%{__cxx}
make -f Makefile.init makefiles dynamicmaps=yes pie=yes \
	shlib_directory="%{_libdir}" \
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

# install chroot script and postfinger
install -m 0755 %{SOURCE14} %{buildroot}%{_sbindir}/postfix-chroot.sh
install -m 0755 %{SOURCE21} %{buildroot}%{_sbindir}/postfinger

# install qshape
install -m755 auxiliary/qshape/qshape.pl %{buildroot}%{_sbindir}/qshape
cp man/man1/qshape.1 %{buildroot}%{_mandir}/man1/qshape.1

# systemd
mkdir -p %buildroot/lib/systemd/system
install -c -m 644 %SOURCE100 %buildroot/lib/systemd/system/
install -m 755 %{SOURCE101} %{buildroot}%{_sysconfdir}/postfix/aliasesdb
install -m 755 %{SOURCE102} %{buildroot}%{_sysconfdir}/postfix/chroot-update
install -d %{buildroot}%{_presetdir}
cat > %{buildroot}%{_presetdir}/86-postfix.preset << EOF
enable postfix.service
EOF

# RPM compresses man pages automatically.
# - Edit postfix-files to reflect this, so post-install won't get confused
#   when called during package installation.
sed -i -e "s@\(/man[158]/.*\.[158]\):@\1%{_extension}:@" %{buildroot}%{_sysconfdir}/postfix/postfix-files

# remove files that are not in the main package
sed -i -e "/dict_.*\.so/d" %{buildroot}%{_sysconfdir}/postfix/postfix-files

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
#ensure the db files are created
%{_sbindir}/postmap /etc/postfix/virtual
%{_sbindir}/postmap /etc/postfix/domains
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
%systemd_postun_with_restart %{name}.service

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
%config(noreplace) %{_sysconfdir}/postfix/domains
%{_sysconfdir}/postfix/chroot-update
%{_sysconfdir}/postfix/aliasesdb
%{_sysconfdir}/postfix/makedefs.out
%config(noreplace) %{_sysconfdir}/postfix/dynamicmaps.cf
%{_presetdir}/86-postfix.preset
%attr(0644, root, root) %{_unitdir}/%{name}.service
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

%dir %{_libexecdir}/postfix
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
%attr(0755, root, root) %{_libexecdir}/postfix/nqmgr
%attr(0755, root, root) %{_libexecdir}/postfix/oqmgr
%attr(0755, root, root) %{_libexecdir}/postfix/pickup
%attr(0755, root, root) %{_libexecdir}/postfix/pipe
%attr(0755, root, root) %{_libexecdir}/postfix/postfix-script
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
%attr(0755, root, root) %{_sbindir}/postfinger
%attr(0755, root, root) %{_sbindir}/postfix-chroot.sh
%attr(0755, root, root) %{_sbindir}/qshape
%attr(0755, root, root) %{sendmail_command}
%{_bindir}/mailq
%{_bindir}/newaliases
%attr(0755, root, root) %{_bindir}/rmail
%{_mandir}/man1/*
%{_mandir}/man5/*
%{_mandir}/man8/*

%files -n %{libdns}
%{_libdir}/postfix/libpostfix-dns.so

%files -n %{libglobal}
%{_libdir}/postfix/libpostfix-global.so

%files -n %{libmaster}
%{_libdir}/postfix/libpostfix-master.so

%files -n %{libutil}
%{_libdir}/postfix/libpostfix-util.so

%files -n %{libtls}
%{_libdir}/postfix/libpostfix-tls.so

%if %{with ldap}
%files ldap
%attr(755, root, root) %{_libdir}/postfix/postfix-ldap.so

%post ldap
%dynmap_add_cmd ldap
%postun ldap
%dynmap_rm_cmd ldap
%endif

%if %{with mysql}
%files mysql
%attr(755, root, root) %{_libdir}/postfix/postfix-mysql.so

%post mysql
%dynmap_add_cmd mysql
%postun mysql
%dynmap_rm_cmd mysql
%endif

%if %{with sdbm}
%files sdbm
%attr(755, root, root) %{_libdir}/postfix/postfix-sdbm.so

%post sdbm
%dynmap_add_cmd sdbm
%postun sdbm
%dynmap_rm_cmd sdbm
%endif

%if %{with pcre}
%files pcre
%attr(755, root, root) %{_libdir}/postfix/postfix-pcre.so

%post pcre
%dynmap_add_cmd pcre
%postun pcre
%dynmap_rm_cmd pcre
%endif

%if %{with pgsql}
%files pgsql
%attr(755, root, root) %{_libdir}/postfix/postfix-pgsql.so

%post pgsql
%dynmap_add_cmd pgsql
%postun pgsql
%dynmap_rm_cmd pgsql
%endif

%if %{with sqlite}
%files sqlite
%attr(755, root, root) %{_libdir}/postfix/postfix-sqlite.so

%post sqlite
%dynmap_add_cmd sqlite
%postun sqlite
%dynmap_rm_cmd sqlite
%endif

%if %{with cdb}
%files cdb
%attr(755, root, root) %{_libdir}/postfix/postfix-cdb.so

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
%{_sysconfdir}/postfix/main.cf.proto
%{_sysconfdir}/postfix/bounce.cf.default
%config(noreplace) %{_sysconfdir}/postfix/master.cf
%attr(0644, root, root) %{_sysconfdir}/postfix/master.cf.proto

