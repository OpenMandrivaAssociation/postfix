%define _disable_ld_no_undefined 1
%define libname %mklibname postfix 1
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
Version:	2.9.4
Release:	1
License:	IBM Public License
Group:		System/Servers
URL:		http://www.postfix.org/
Source0: 	ftp://ftp.porcupine.org/mirrors/postfix-release/official/%{name}-%{version}.tar.gz
Source1: 	%{SOURCE0}.sig
Source2: 	postfix-main.cf
Source3: 	postfix-etc-init.d-postfix
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

BuildRequires:	db-devel
BuildRequires:	gawk
BuildRequires:	perl-base
BuildRequires:	sed
BuildRequires:	html2text
%if %{with sasl}
BuildRequires:	libsasl-devel >= 2.0
%endif
%if %{with tls}
BuildRequires:	openssl-devel >= 0.9.7
%endif

Provides:	mail-server
Provides:	sendmail-command
# syslog-ng before this version needed a different chroot script, 
# which was bug-prone
Conflicts:	syslog-ng < 3.1-0.beta2.2
# http://archives.mandrivalinux.com/cooker/2005-06/msg01987.php
Requires(post): chkconfig
Requires: initscripts
Requires: syslog-daemon
Requires: coreutils
Requires: diffutils
Requires: gawk
Requires(pre,post,postun,preun): rpm-helper >= 0.3
Requires(pre,post):	sed
%if %{with tls}
Requires(post):	openssl
%endif
Requires(post,preun): update-alternatives
Requires(post,preun): %{libname} >= %EVRD
Requires: %name-config >= 2.9.0-1

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
Requires:	%{name} = %EVRD

%description ldap
This package provides support for LDAP maps in Postfix.
%endif

%if %{with pcre}
%package pcre
Summary:	PCRE map support for Postfix
Group:		System/Servers
BuildRequires:	pcre-devel
Requires:	%{name} = %EVRD

%description pcre
This package provides support for PCRE (perl compatible regular expression)
maps in Postfix.
%endif

%if %{with mysql}
%package mysql
Summary:	MYSQL map support for Postfix
Group:		System/Servers
BuildRequires:	mysql-devel
Requires:	%{name} = %EVRD

%description mysql
This package provides support for MYSQL maps in Postfix.
%endif

%if %{with pgsql}
%package pgsql
Summary:	Postgres SQL map support for Postfix
Group:		System/Servers
BuildRequires:	postgresql9.0-devel
Requires:	%{name} = %EVRD

%description pgsql
This package provides support for Postgres SQL maps in Postfix.
%endif

%if %{with sqlite}
%package sqlite
Summary:	SQLite map support for Postfix
Group:		System/Servers
BuildRequires:	sqlite3-devel
Requires:	%{name} = %EVRD

%description sqlite
This package provides support for SQLite maps in Postfix.
%endif

%if %{with cdb}
%package cdb
Summary:	CDB map support for Postfix
Group:		System/Servers
BuildRequires:	libtinycdb-devel
Requires:	%{name} = %EVRD

%description cdb
This package provides support for CDB maps in Postfix.
%endif

%package config-standalone
Summary: Default configuration files for running Postfix standalone
Provides: %name-config = %version-%release
Conflicts: %name-config-dovecot

%description config-standalone
Default configuration files for running Postfix standalone.

Use this config if you intend to run Postfix without dovecot.
Alternatively, install %name-config-dovecot for the
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
	sed -i -e "s@/lib/@/%{_lib}@g" conf/main.cf
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
rm -fr %{buildroot}

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

# This installs into the /etc/rc.d/init.d directory
mkdir -p %{buildroot}%{_initrddir}
install -c %{SOURCE3} %{buildroot}%{_initrddir}/postfix
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
%attr(0755, root, root) %{_initrddir}/postfix
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
%{_mandir}/*/*

%files -n %{libname}
%attr(0755, root, root) %{_libdir}/libpostfix-dns.so.1
%attr(0755, root, root) %{_libdir}/libpostfix-global.so.1
%attr(0755, root, root) %{_libdir}/libpostfix-master.so.1
%attr(0755, root, root) %{_libdir}/libpostfix-util.so.1
%attr(0755, root, root) %{_libdir}/libpostfix-tls.so.1
%attr(0755, root, root) %{_libdir}/libpostfix-milter.so.1
%attr(0755, root, root) %{_libdir}/libpostfix-xsasl.so.1

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


%changelog
* Fri Aug 03 2012 Bernhard Rosenkraenzer <bero@bero.eu> 1:2.9.4-1
+ Revision: 811686
- Split config file into separate package so we can provide an alternate default
  config for the postfix+dovecot+amavisd-new combo
- Update to 2.9.4

* Mon May 21 2012 Bernhard Rosenkraenzer <bero@bero.eu> 1:2.9.3-1
+ Revision: 799763
- Update to 2.9.3
- Fix bug #65571

* Sat May 12 2012 Bernhard Rosenkraenzer <bero@bero.eu> 1:2.9.2-1
+ Revision: 798525
- Update to 2.9.2

* Fri May 11 2012 Bernhard Rosenkraenzer <bero@bero.eu> 1:2.9.1-1
+ Revision: 798291
- Update to 2.9.1
- Add sqlite support in dynamicmaps

* Fri May 11 2012 Crispin Boylan <crisb@mandriva.org> 1:2.8.7-4
+ Revision: 798194
- Rebuild

* Tue Feb 07 2012 Oden Eriksson <oeriksson@mandriva.com> 1:2.8.7-3
+ Revision: 771526
- rebuilt for new pcre

* Thu Dec 29 2011 Luca Berra <bluca@mandriva.org> 1:2.8.7-2
+ Revision: 748167
- fixed creation of /etc/sysconfig/postfix on clean install (#65025)
- added openssl dependancy for certificate generation on install

* Wed Dec 14 2011 Matthew Dawkins <mattydaw@mandriva.org> 1:2.8.7-1
+ Revision: 740867
- added back require post preun for lib pkg
- last details for clean up
- more spec clean ups
- alternatives has been default since 2007
- converted format_not_a_string.... patch to p1
- employed apply_patches
- removed unneeded check for version release date
- cleaned up description
- removed legacy sources 16 & 17
- new version 2.8.7
- major spec clean up
- should be cross distro compatible
- removed pre 201001 legacy build support
- dynamicmaps has been default since 200701
- added workaround for serverbuild macro fPIE
- removed experimental build support
- new release date 20111024 (not sure really needed anymore)
- employed EVRD macro

* Tue Oct 25 2011 Luis Daniel Lucio Quiroz <dlucio@mandriva.org> 1:2.8.6-2
+ Revision: 707171
- SPEC fixes,
  some modifications to make compatible this SPEC with mageia, not finished yet

* Tue Oct 25 2011 Luis Daniel Lucio Quiroz <dlucio@mandriva.org> 1:2.8.6-1
+ Revision: 707154
- 2.8.6

* Thu May 19 2011 Per Øyvind Karlsen <peroyvind@mandriva.org> 1:2.8.3-2
+ Revision: 676158
- use %%{_extension} for getting correct man page compression extension

* Tue May 17 2011 Oden Eriksson <oeriksson@mandriva.com> 1:2.8.3-1
+ Revision: 675688
- 2.8.3
- rediff the debian patches (P0, P1, P3)
- P11: fix format string errors

* Tue May 17 2011 Oden Eriksson <oeriksson@mandriva.com> 1:2.7.4-1
+ Revision: 675366
- 2.7.4 (fixes CVE-2011-1720)

* Mon Apr 11 2011 Funda Wang <fwang@mandriva.org> 1:2.7.3-4
+ Revision: 652494
- br db 5.1

* Tue Mar 22 2011 Luca Berra <bluca@mandriva.org> 1:2.7.3-3
+ Revision: 647660
- create /dev/urandom in chroot (#62851)

* Thu Mar 17 2011 Oden Eriksson <oeriksson@mandriva.com> 1:2.7.3-2
+ Revision: 645753
- relink against libmysqlclient.so.18

* Wed Mar 09 2011 Oden Eriksson <oeriksson@mandriva.com> 1:2.7.3-1
+ Revision: 643117
- 2.7.3

* Thu Feb 24 2011 Oden Eriksson <oeriksson@mandriva.com> 1:2.7.2-1
+ Revision: 639550
- 2.7.2

* Sat Jan 01 2011 Oden Eriksson <oeriksson@mandriva.com> 1:2.7.1-3mdv2011.0
+ Revision: 627041
- fix bork
- rebuilt against mysql-5.5.8 libs, again

* Mon Dec 27 2010 Oden Eriksson <oeriksson@mandriva.com> 1:2.7.1-2mdv2011.0
+ Revision: 625425
- rebuilt against mysql-5.5.8 libs

* Sun Oct 03 2010 Luca Berra <bluca@mandriva.org> 1:2.7.1-1mdv2011.0
+ Revision: 582776
- disable some unneeded and potentially harmful nss libraries in /etc/sysconfig/postfix
  enable ssl by default and create dummy certs

  + Matthew Dawkins <mattydaw@mandriva.org>
    - new version 2.7.1
      rediffed patch3

* Mon Apr 05 2010 Funda Wang <fwang@mandriva.org> 1:2.7.0-4mdv2010.1
+ Revision: 531715
- rebuild for new openssl

  + Luca Berra <bluca@mandriva.org>
    - fix an harmless warning in postun

* Tue Mar 02 2010 Michael Scherer <misc@mandriva.org> 1:2.7.0-3mdv2010.1
+ Revision: 513544
- listen to ipv6 if availiable

* Fri Feb 26 2010 Oden Eriksson <oeriksson@mandriva.com> 1:2.7.0-2mdv2010.1
+ Revision: 511619
- rebuilt against openssl-0.9.8m

* Sat Feb 20 2010 Luca Berra <bluca@mandriva.org> 1:2.7.0-1mdv2010.1
+ Revision: 508819
- new version 2.7.0
  split dynamicmaps sdbm and dbupgrade
  postfix-cdb is now a separate package
  remove requirement for 'ed'
  use default ldflags
  update alternatives remove command according to policy
  misc spec fixes

* Wed Feb 17 2010 Oden Eriksson <oeriksson@mandriva.com> 1:2.6.5-5mdv2010.1
+ Revision: 507037
- rebuild

* Sun Jan 24 2010 Luca Berra <bluca@mandriva.org> 1:2.6.5-4mdv2010.1
+ Revision: 495526
- fix removing of syslog-ng configuration
- enable support for cdb databases
- removed fixup for alternatives problem prior to 2006.0
  support more map types in initscript
  support for /etc/syslog-ng.d in chroot script

* Fri Jan 01 2010 Oden Eriksson <oeriksson@mandriva.com> 1:2.6.5-3mdv2010.1
+ Revision: 484730
- rebuilt against bdb 4.8

* Sun Oct 11 2009 Luca Berra <bluca@mandriva.org> 1:2.6.5-2mdv2010.0
+ Revision: 456675
- make ip-up scripts multi-instance aware and move ifup script to resolvconf
- make initscript and postfix-chroot.sh multi-instance aware
- fix postmulti behaviour when iterating over disabled instances
- update vda-ng patch to 2.6.5
- reenable default content filters in master.cf
- load dynamicmaps.cf from default config directory only

* Mon Aug 31 2009 Frederik Himpe <fhimpe@mandriva.org> 1:2.6.5-1mdv2010.0
+ Revision: 423044
- Update to new version 2.6.5

* Wed Jul 15 2009 Luca Berra <bluca@mandriva.org> 1:2.6.2-1mdv2010.0
+ Revision: 396453
- Updated to 2.6.2
- WARNING: the postfix-chroot script is not yet updated to new multi-instance

* Fri May 22 2009 Eugeni Dodonov <eugeni@mandriva.com> 1:2.5.7-1mdv2010.0
+ Revision: 378744
- Updated to 2.5.7.
  Updated chroot script to prevent bogus error message.

* Sun Mar 29 2009 Luca Berra <bluca@mandriva.org> 1:2.5.6-4mdv2009.1
+ Revision: 362144
- add some comments to /etc/posyfix-syslog-ng.conf file
- postfix-chroot.sh: update rsyslog configuration with chroot path found at runtime, not hardcoded (allow user to change spool dir)
- postfix-chroot.sh: insert a note stating that rsyslog and syslog-ng changes are not multi-instance aware
- revert change 338316 which prevented chrooted postfix from logging with syslog-ng
  rework change 338317 to allow postfix to work with both syslog-ng v2 configuration (<2009.1) and v3 (2009.1 and above)

* Thu Mar 05 2009 Eugeni Dodonov <eugeni@mandriva.com> 1:2.5.6-3mdv2009.1
+ Revision: 349129
- Prevent restarting rsyslog twice during installation.

* Thu Mar 05 2009 Eugeni Dodonov <eugeni@mandriva.com> 1:2.5.6-2mdv2009.1
+ Revision: 349028
- Added support for logging to rsyslog.

  + Raphaël Gertz <rapsys@mandriva.org>
    - Fix destination naming too (break syslog-ng startup)
    - Remove the syslog-ng v3 configuration file break

* Tue Jan 06 2009 Jérôme Soyer <saispo@mandriva.org> 1:2.5.6-1mdv2009.1
+ Revision: 325400
- update to new version 2.5.6

* Thu Dec 18 2008 Luca Berra <bluca@mandriva.org> 1:2.5.5-5mdv2009.1
+ Revision: 315529
- create dev directory into chroot when using syslog-ng (#46461)

* Wed Dec 17 2008 Oden Eriksson <oeriksson@mandriva.com> 1:2.5.5-4mdv2009.1
+ Revision: 315246
- rediffed fuzzy patches
- use lowercase mysql-devel

* Sat Dec 06 2008 Oden Eriksson <oeriksson@mandriva.com> 1:2.5.5-3mdv2009.1
+ Revision: 311203
- rebuilt against mysql-5.1.30 libs

* Tue Sep 16 2008 Luca Berra <bluca@mandriva.org> 1:2.5.5-2mdv2009.0
+ Revision: 285171
+ rebuild (emptylog)

* Wed Sep 03 2008 Frederik Himpe <fhimpe@mandriva.org> 1:2.5.5-1mdv2009.0
+ Revision: 279878
- update to new version 2.5.5

* Mon Aug 18 2008 Luca Berra <bluca@mandriva.org> 1:2.5.4-1mdv2009.0
+ Revision: 273221
- update vda patch
- updated to version 2.5.4 (fix CVE-2008-2936)

* Tue Jul 29 2008 Oden Eriksson <oeriksson@mandriva.com> 1:2.5.3-1mdv2009.0
+ Revision: 252711
- fix releasedate 20080726
- 2.5.3
- hardcode %%{_localstatedir}

* Fri Jul 18 2008 Guillaume Rousse <guillomovitch@mandriva.org> 1:2.5.2-5mdv2009.0
+ Revision: 238168
- fix multiple inclusions in syslog-ng configuration, but checking for actual configuration directive, not added markers

* Tue Jul 15 2008 Guillaume Rousse <guillomovitch@mandriva.org> 1:2.5.2-4mdv2009.0
+ Revision: 236205
- fix multiple inclusions in syslog-ng configuration

* Wed Jul 09 2008 Guillaume Rousse <guillomovitch@mandriva.org> 1:2.5.2-3mdv2009.0
+ Revision: 233049
- fix syslog-ng configuration stanza in chroot setup script

  + Pixel <pixel@mandriva.com>
    - do not call ldconfig in %%post/%%postun, it is now handled by filetriggers

* Fri Jun 06 2008 Guillaume Rousse <guillomovitch@mandriva.org> 1:2.5.2-2mdv2009.0
+ Revision: 216435
- compatibility with syslog-ng too

  + Pixel <pixel@mandriva.com>
    - adapt to %%_localstatedir now being /var instead of /var/lib (#22312)

* Sun May 18 2008 Oden Eriksson <oeriksson@mandriva.com> 1:2.5.2-1mdv2009.0
+ Revision: 208715
- 2.5.2

  + Luca Berra <bluca@mandriva.org>
    - add some missing requires (#40079)
    - postfix should be started after saslauthd (#36943)

* Thu Apr 17 2008 Oden Eriksson <oeriksson@mandriva.com> 1:2.5.1-4mdv2009.0
+ Revision: 195185
- bump release
- revert the "conform to the 2008 specs (don't start the services per
  default)" changes and let this be handled some other way...

* Wed Mar 26 2008 Oden Eriksson <oeriksson@mandriva.com> 1:2.5.1-2mdv2008.1
+ Revision: 190296
- don't start it per default

* Mon Feb 25 2008 Andreas Hasenack <andreas@mandriva.com> 1:2.5.1-1mdv2008.1
+ Revision: 174896
- drop unnaplied patches
- updated to version 2.5.1

* Mon Jan 28 2008 Andreas Hasenack <andreas@mandriva.com> 1:2.5.0-1mdv2008.1
+ Revision: 159399
- updated to version 2.5.0
- don't call post-install directly
  (http://thread.gmane.org/gmane.mail.postfix.user/177210/focus=177230)

  + Olivier Blin <blino@mandriva.org>
    - restore BuildRoot

* Fri Dec 21 2007 Oden Eriksson <oeriksson@mandriva.com> 1:2.4.6-2mdv2008.1
+ Revision: 136277
- rebuilt against bdb 4.6.x libs

  + Thierry Vignaud <tv@mandriva.org>
    - kill re-definition of %%buildroot on Pixel's request

* Mon Oct 22 2007 Andreas Hasenack <andreas@mandriva.com> 1:2.4.6-1mdv2008.1
+ Revision: 101118
- updated to version 2.4.6

  + Luca Berra <bluca@mandriva.org>
    - fix with/without description

* Thu Aug 23 2007 Thierry Vignaud <tv@mandriva.org> 1:2.4.5-2mdv2008.0
+ Revision: 70044
- fileutils, sh-utils & textutils have been obsoleted by coreutils a long time ago

* Wed Aug 01 2007 Andreas Hasenack <andreas@mandriva.com> 1:2.4.5-1mdv2008.0
+ Revision: 57633
- updated to version 2.4.5
- updated to version 2.4.4
- adjusted docdir to new policy
- adjusted manpage file list to new compression if needed,
  depending on distro version

* Fri Jun 22 2007 Andreas Hasenack <andreas@mandriva.com> 1:2.4.3-2mdv2008.0
+ Revision: 43194
- proper user of serverbuild macro

* Thu May 31 2007 Andreas Hasenack <andreas@mandriva.com> 1:2.4.3-1mdv2008.0
+ Revision: 33435
- updated to version 2.4.3

* Wed May 02 2007 Andreas Hasenack <andreas@mandriva.com> 1:2.4.1-1mdv2008.0
+ Revision: 20524
- updated to version 2.4.1

* Thu Mar 08 2007 Andreas Hasenack <andreas@mandriva.com> 2.3.8-1mdv2007.1
+ Revision: 138350
- updated to version 2.3.8

* Sat Feb 17 2007 Luca Berra <bluca@mandriva.org> 1:2.3.7-2mdv2007.1
+ Revision: 122086
- disable additional restrictions in filter reinjection service (#28632)
- do not chroot spawn service

  + Andreas Hasenack <andreas@mandriva.com>
    - updated to version 2.3.7
    - enabled gcc's stack protector feature, let's experiment with it

* Sat Jan 06 2007 Andreas Hasenack <andreas@mandriva.com> 1:2.3.6-1mdv2007.1
+ Revision: 104810
- updated to version 2.3.6

* Tue Jan 02 2007 Andreas Hasenack <andreas@mandriva.com> 1:2.3.5-1mdv2007.1
+ Revision: 103126
- updated to version 2.3.5
- redid multi_instance patch for this version
- removed version number from patch name, so we can easily see
  the diff in the future
- remove svn warning

* Mon Nov 06 2006 Andreas Hasenack <andreas@mandriva.com> 1:2.3.4-1mdv2007.0
+ Revision: 76969
- updated to version 2.3.4

  + Luca Berra <bluca@mandriva.org>
    - override umask in postfix-chroot.sh (#26860)
    - fix copying of nss libs in chroot (#26587)
    - fix an error in multi_instance patch
    - add post,preun requires for library (fix deinstallation)
    - updated multi_instance patch
    - fix for rpm overwriting sasl config file
    - small update to README.MDK

* Tue Sep 12 2006 Luca Berra <bluca@mandriva.org> 1:2.3.3-4mdv2007.1
+ Revision: 60882
-4mdv

* Sat Sep 09 2006 Luca Berra <bluca@mandriva.org> 1:2.3.3-3mdv2007.1
+ Revision: 60628
- remove requires on file-name
- updated vda patch

* Fri Sep 01 2006 Luca Berra <bluca@mandriva.org> 1:2.3.3-2mdv2007.1
+ Revision: 59265
-2mdv
- updated ip-up/down and ifup scripts
- updated content-filter default configurations

* Tue Aug 29 2006 Andreas Hasenack <andreas@mandriva.com> 1:2.3.3-1mdv2007.0
+ Revision: 58394
- updated to version 2.3.3
- fix default sasl path/filename

  + Luca Berra <bluca@mandriva.org>
    - remove old patches
    - fix a typo in sasl fix
    - fix for new location of sasl configuration file

* Tue Aug 08 2006 Andreas Hasenack <andreas@mandriva.com> 1:2.3.2-1mdv2007.0
+ Revision: 54229
- merged in work done on branch 2.3.2:
- remove in from dynamicmaps.cf in %%post the maps we don't have as dynamic objects
  anymore (cidr, tcp and sdbm)
- bunzipped postfinger and postfix-chroot
- missed one slave_config_directories 2>/dev/null in postfix-chroot.sh
- send postconf errors to /dev/null in the initscript. Since we don't
  have the multi_instance patch applied yet, the disable_start and
  slave_config_directories configuration directives don't exist and
  postfix was warning us about it
- make milter and xsasl also dynamic
- final (I hope) adjustments to dynamicmaps patch
- updated mdkconfig patch for this version: some hunks conflict
  with the dynamicmaps patch
- dropped dynamic cidr, sdbm and tcp maps. As far as I can see, they
  don't bring in new dependencies and were always loaded by default
  anyway
- updated dynamic map patch
- update dynamic patch, taken from debian's 2.3.1 package
- removed saslpath patch, no longer needed (postfix has this directive
  upstream now)
- removed dbupgrade patch for now, it may be already applied (got some
  "reverse" warnings from patch but didn't check yet)
- updated multiline greeting patch to 2.3.2
- preliminary update of the sasl_loggin patch: one hunk is no longer needed
  (applied upstream), the other is still not working
- removed rejectstrip patch/build option, already applied upstream
- updated multi_instance patch to 2.3-20060616, doesn't apply
- removed kolab2 patches, already applied
- adjust build to use cyrus-sasl by default instead of dovecot

* Wed Jul 26 2006 Andreas Hasenack <andreas@mandriva.com> 1:2.2.11-1mdv2007.0
+ Revision: 42152
- updated to version 2.2.11
- adjusted postgresql-devel buildrequires to require a
  minimum version (see comment in SPEC file and RELEASE NOTES)
- fix default sasl database path in the sample configuration file
- import postfix-2.2.10-5mdv2007.0

* Wed Jun 21 2006 Oden Eriksson <oeriksson@mandriva.com> 1:2.2.10-5mdv2007.0
- don't use "delay_warning_time = 4h" per default (#23198)

* Mon Jun 19 2006 Luca Berra <bluca@vodka.it> 1:2.2.10-4mdv2007.0
- fix bug in postfix-chroot script that would remove real files
  instead of chroot copies
- temporary fix for smtpd_sasl_path and new sasl with
  SASL_CB_GETCONFPATH callback

* Mon Jun 05 2006 Luca Berra <bluca@vodka.it> 1:2.2.10-3mdv2007.0
- new macros for conditionals
- fix /etc/pam.d/smtp
- add multi_instance patch
- make postfix-chroot script multi_instance aware
- make map rebuild in initscript multi_instance aware and user configurable
- lsb-ize initscript
- update vda patch (still not applied by default)
- update Jim Seymour stuff
- update README.MDK

* Tue May 16 2006 Stefan van der Eijk <stefan@eijk.nu> 1:2.2.10-2mdk
- rebuild for sparc

* Fri Apr 07 2006 Andreas Hasenack <andreas@mandriva.com> 1:2.2.10-1mdk
- updated to version 2.2.10

* Sun Feb 26 2006 Luca Berra <bluca@vodka.it> 1:2.2.9-2mdk
- changed some leftovr references to Mandrakelinux (#21286)
- main.cf.dist is now the unadultered version shipped with postfix source.

* Fri Feb 24 2006 Andreas Hasenack <andreas@mandriva.com> 1:2.2.9-1mdk
- updated to version 2.2.9

* Thu Jan 05 2006 Oden Eriksson <oeriksson@mandriva.com> 1:2.2.8-1mdk
- 2.2.8 (Minor bugfixes)

* Thu Dec 29 2005 Oden Eriksson <oeriksson@mandriva.com> 1:2.2.7-1mdk
- 2.2.7

* Wed Nov 30 2005 Andreas Hasenack <andreas@mandriva.com> 1:2.2.6-1mdk
- updated to version 2.2.6

* Sun Nov 13 2005 Oden Eriksson <oeriksson@mandriva.com> 2.2.5-9mdk
- rebuilt against openssl-0.9.8a

* Sun Oct 30 2005 Oden Eriksson <oeriksson@mandriva.com> 2.2.5-8mdk
- rebuilt against MySQL-5.0.15

* Wed Sep 07 2005 Oden Eriksson <oeriksson@mandriva.com> 2.2.5-7mdk
- rebuild

* Wed Aug 31 2005 Buchan Milne <bgmilne@linux-mandrake.com> 2.2.5-6mdk
- Rebuild for new libldap-2.3
- buildrequire openldap-devel, not libldap-devel
- use 1 instead of %%prel for rpmbuildupdate to work nicely

* Wed Aug 10 2005 Leonardo Chiquitto Filho <chiquitto@mandriva.com> 1:2.2.5-5.mdk
- added kolab2 ldap-leafonly patch, which was sent upstream but still
  wasn't applied to 2.3. Only gets applied when with_KOLAB == 1 (which is
  the default)
- by andreas:
  - Prereq -> Requires(foo)
  - Requires(foo,bar) -> Requires(foo) and Requires(bar)

* Thu Jul 28 2005 Andreas Hasenack <andreas@mandriva.com> 1:2.2.5-4mdk
- added "ed" to requires
- small change to the documentation part of the kolab2 patch (which is
  still not applied by default)

* Wed Jul 27 2005 Andreas Hasenack <andreas@mandriva.com> 1:2.2.5-3mdk
- added kolab2 nullsender patch, backported from postfix-2.3 (disabled by
  default: awaiting further testing)
- fixed company name (#17048)

* Sat Jul 23 2005 Andreas Hasenack <andreas@mandriva.com> 1:2.2.5-2mdk
- rebuilt with libdb-4.2 instead of 4.3

* Sat Jul 23 2005 Andreas Hasenack <andreas@mandriva.com> 1:2.2.5-1mdk
- updated to version 2.2.5
- removed %%config tag from postfix-script, post-install, main.cf.dist,
  makedefs.out and postfix-files. These files *have* to be overwritten during
  an upgrade, they are not configuration files from older versions that can
  remain.
  - post-install: performs upgrades and checks. Needs to be the new version
    always.
  - postfix-script: postfix command script
  - main.cf.dist: defaults from the distribution
  - makedefs.out: shows how this postfix was built
  - postfix-files: files from the distribution, ownership and permissions
  Unfortunately, this change will only be complete in future upgrades,
  since these files in previous packages were %%config

* Wed Jul 20 2005 Andreas Hasenack <andreas@mandriva.com> 1:2.2.4-6mdk
- got rid of mta alternatives
- implemented sendmail-command alternatives
- added warning in %%pre about possible breakage. Also as README.MDK.update
  in %%doc
- added fix in the init script to deal with the most serious issues
  caused by the alternatives breakage, including creating a missing
  /usr/bin/rmail script if needed
- fixed default alias_database and alias_maps (there was a missing hunk
  the mdkconfig patch)

* Tue Jul 19 2005 Andreas Hasenack <andreas@mandriva.com> 1:2.2.4-5mdk
- updated strip/reject patch
- removed %%config tag altogether from the main.cf.default file

* Wed Jul 13 2005 Andreas Hasenack <andreas@mandriva.com> 1:2.2.4-4mdk
- included optional CDB support in the build (disabled by default).
  Thanks to akukula@gmail.com for the suggestion.
- disabled alternatives trigger, even though this will still haunt us for a
  while
- fixed typo in content filter in master.cf (#15264)
- added reject_strip patch (build conditionally: default is yes for now)
- added sasl_authenticated_header patch from Branko F. Gra�nar <bfg@noviforum.si>
- removed "default" from %%config for the main.cf.default file. It's still a
  %%config file, but new versions have new defaults.

* Tue Jul 12 2005 Andreas Hasenack <andreas@mandriva.com> 1:2.2.4-3mdk
- provides mail-server and sendmail-command (removed older provides).
  See http://archives.mandrakelinux.com/cooker/2005-06/msg01987.php
  The alternatives change will come in the next release

* Tue Jul 05 2005 Andreas Hasenack <andreas@mandriva.com> 1:2.2.4-2mdk
- removed sample_directory from main.cf since these files are no longer
  supplied with postfix (#15297). Note that the now obsolete parameter
  still exists, however, and its default value is /etc/postfix
- fixed build without TLS (note that tlsmgr and libpostfix-tls still get
  built, but without TLS support [go figure])

* Tue Jul 05 2005 Andreas Hasenack <andreas@mandriva.com> 1:2.2.4-1mdk
- updated to version 2.2.4, added signed tarball
- updated the dynamic maps patch from debian's 2.2.3 postfix package
- removed tls and ipv6 patches (pfix 2.2.x already includes those)
- TLS and IPv6 are enabled by default
- updated the dbupgrade patch
- package now builds also when dynamicmaps is disabled
- redid mdkconfig patch for this version
- redid saslpath patch for this version
- redid smtpstone patch for this version
- not applying the postfix-smtp_sasl_proto.c patch for now: I would like
  to test this since it's a very old patch
- updated VDA patch
- updated postfinger to version 1.30
- removed %%config mark from the init script: we should only use the
  sysconfig file for configuring the init script

* Wed Jun 15 2005 Frederic Lepied <flepied@mandriva.com> 2.1.5-7mdk
- fix prereq
- rebuild for libpq

* Wed Mar 16 2005 Luca Berra <bluca@vodka.it> 2.1.5-6mdk
- upgrade ipv6 patch to 1.26 (possible secuirity issue)
- provide a default /etc/postfix/sasl/smtpd.conf
- updated README.MDK
- updated postfix-users faq

* Fri Feb 04 2005 Buchan Milne <bgmilne@linux-mandrake.com> 2.1.5-5mdk
- rebuild for ldap2.2_7

* Sat Jan 22 2005 Luca Berra <bluca@vodka.it> 2.1.5-4mdk
- include man page for qshape (bugzilla #13119)

* Sat Jan 15 2005 Luca Berra <bluca@vodka.it> 2.1.5-2mdk
- use distro specific release tags
- updated README.MDK
- provide a default /etc/pam.d/smtp for saslauthd users
- don't move sasl conf if not necessary
- make main.cf.dist a working config file
- enable xforward for content filters (e.g. recent amavisd-new)

* Fri Dec 10 2004 Rafael Garcia-Suarez <rgarciasuarez@mandrakesoft.com> 2.1.5-2mdk
- s/Mandrake Linux/Mandrakelinux/ in default conf and docs

* Sun Nov 28 2004 Luca Berra <bluca@vodka.it> 2.1.5-1mdk 
- 2.1.5
- fix creation of aliases at startup
- do not refresh aliases at install time
- use tls+ipv6 instead of tls
- now requires html2text to build documentation

* Sun Aug 29 2004 Luca Berra <bluca@vodka.it> 2.1.4-2mdk 
- rebuilt with db-4.2

* Mon Aug 09 2004 Luca Berra <bluca@vodka.it> 2.1.4-1mdk 
- 2.1.4 (should fix problems for ppc users)
- added vda patch (disabled in default build)
- reworked map creation at startup, to catch parameters postconf won't show

* Fri Jul 30 2004 Stew Benedict <sbenedict@mandrakesoft.com> 2.1.1-2mdk 
- sendmail symlink needs to be in /usr/lib (LSB)

* Tue May 04 2004 Luca Berra <bluca@vodka.it> 2.1.1-1mdk 
- 2.1.1
- pfixtls-0.8.18-2.1.0-0.9.7d
- added p4 (tls docs)
- touch readmes so it does not try to rebuild them

* Mon Apr 26 2004 Luca Berra <bluca@vodka.it> 2.1.0-1mdk 
- 2.1.0 release
- rediffed p0, p1, p5, p6, tls
- dropped p14, p16
- goodbye samples, hello html documentation
- included qshape
- updated postfinger, postfix faq, Jim Seymour's stuff
- fixed map creation at startup (thanks to Andrzej Kukula for ideas)
- check for chroot sanity at startup

