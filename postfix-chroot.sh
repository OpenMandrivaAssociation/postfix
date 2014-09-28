#!/bin/sh
#
# postfix-chroot.sh - enable or disable Postfix chroot
#
# (C) 2003 Luca Berra <bluca@vodka.it>
#
# originally based on postfix-chroot.sh
# (C) 2003 Simon J Mudd <sjmudd@pobox.com>
#
# This script is intended to enable you to enable or disable the Postfix
# chroot environment.
#
# License:
#    This program is free software; you can redistribute it and/or
#    modify it under the terms of the GNU General Public License
#    as published by the Free Software Foundation; either version 2
#    of the License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You may have received a copy of the GNU General Public License
#    along with this program; if not, write to the Free Software
#    Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307,
#    USA.
#
#    An on-line copy of the GNU General Public License can be found
#    http://www.fsf.org/copyleft/gpl.html.

usage () {
    myname=${0##*/}
    cat <<EOF
Usage: $myname [-q|-h] {enable|disable|update|check|check_update}

    Options:
	-h      - this help
	-q      - do not issue action/error messages
    Commands:
	enable  - setup Postfix chroot (removing the previous setup)
	disable - remove Postfix chroot
	update  - update files in Postfix chroot
	check   - check differences between files in chroot and system
	check_update   - check differences between files in chroot and system
	                 and update if needed
EOF
}

# print an error message and exit
error () {
    echo "Error: $@" >&2
    exit 1
}

# print a warning message
warn () {
    echo "Warning: $@" >&2
}

# if $verbose==1 print message ($2) otherwise do nothing
info () {
    [ "$verbose" = 1 ] && echo "$@" >&2 || :
}

# Link source file to chroot directory if possible. If the source is a
# symbolic link, make a copy of the link in the chroot directory,
# otherwise copy the file.
copy() {
    local T L
    if [ -n "$2" ]; then
	T=${chroot%/}/${2#/}
    else
	T=${chroot%/}/${1#/}
    fi
    info "  $1 -> $T"
    mkdir -p ${T%/*}
    if [ -L $1 ]; then
	L=`readlink -f $1`
        ln -sf $L $T
	copy $L
    else
	cp -pf $1 $T
    fi
}

rmtree() {
    local d=${1#$chroot}/
    while [ -n "${d%/*}" ]; do
	rmdir ${chroot}${d} 2>/dev/null || return 1
    done
}    

remove() {
    local L
    local f=${1#$chroot}
    f=${chroot%/}/${f#/}
    if [ -L $f ]; then
	L=`readlink -f $f`
	[ -f ${chroot}$L ] && rm -f ${chroot}$L
	rmtree ${chroot}${L%/*}
	rm -f $f
    elif [ -f $f ];then
	rm -f $f
    fi
    rmtree ${f%/*}
}

# update syslog configuration (rsyslog, sysklogd or syslog-ng)
update_sysklogd() {
    local SYSLOGD_OPTIONS=""
    local NEW_SYSLOGD_OPTIONS=""

    [ -s /etc/sysconfig/syslog ] && . /etc/sysconfig/syslog

    case $1 in
	enable)
	    if ! grep -qs "^[[:space:]]*SYSLOGD_OPTIONS" /etc/sysconfig/syslog ; then
		    info "Adding SYSLOGD_OPTIONS in the /etc/sysconfig/syslog file."
		    echo "SYSLOGD_OPTIONS=\"-a ${chroot}/dev/log\"" >> /etc/sysconfig/syslog
		    service_restart_syslog=1
	    else
		    if ! grep -q "^[[:space:]]*SYSLOGD_OPTIONS=.*-a ${chroot}/dev/log" /etc/sysconfig/syslog; then
		    NEW_SYSLOGD_OPTIONS="${SYSLOGD_OPTIONS} -a ${chroot}/dev/log"
		    sed -i -e "s!^[[:space:]]*SYSLOGD_OPTIONS=.*\$!SYSLOGD_OPTIONS=\"${NEW_SYSLOGD_OPTIONS}\"!" /etc/sysconfig/syslog
		    service_restart_syslog=1
		    fi
	    fi
	    ;;
	disable)
	    NEW_SYSLOGD_OPTIONS="`echo ${SYSLOGD_OPTIONS} | sed -e \"s! *-a ${chroot}/dev/log!!\"`"
	    if [ "${NEW_SYSLOGD_OPTIONS}" != "${SYSLOGD_OPTIONS}" ]; then
		    sed -i -e "s!^[[:space:]]*SYSLOGD_OPTIONS=.*\$!SYSLOGD_OPTIONS=\"${NEW_SYSLOGD_OPTIONS}\"!" /etc/sysconfig/syslog
		    service_restart_syslog=1
	    fi
	    ;;
    esac
}

update_rsyslog() {
# note: we use a single configuration file for all postfix instances, to avoid issue in case an instance is renamed
    case $1 in
	enable)
	    if ! grep -qs "\$AddUnixListenSocket ${chroot}/dev/log" /etc/rsyslog.d/postfix.conf; then
		echo "\$AddUnixListenSocket ${chroot}/dev/log" >> /etc/rsyslog.d/postfix.conf
		service_restart_rsyslog=1
	    fi
	;;
	disable)
	    if grep -qs "\$AddUnixListenSocket ${chroot}/dev/log" /etc/rsyslog.d/postfix.conf; then
		sed -i -e "\!\$AddUnixListenSocket ${chroot}/dev/log!d" /etc/rsyslog.d/postfix.conf
		[ -f /etc/rsyslog.d/postfix.conf -a ! -s /etc/rsyslog.d/postfix.conf ] && rm -f /etc/rsyslog.d/postfix.conf
		service_restart_rsyslog=1
	    fi
	;;
    esac
}
update_syslogng_old() {
    case $1 in
	enable)
	    if ! grep -q -E "(unix-stream|file)[[:space:]]*\([[:space:]]*([\"'])${chroot}/dev/log\2" /etc/syslog-ng.conf; then
		if [ ! -e ${confdir}/syslog-ng.conf ]; then
		    warn "cannot find ${confdir}/syslog-ng.conf, instance will not log properly"
		elif [ -s ${confdir}/syslog-ng.conf ]; then
		    sed -e "s!@CHROOT@!${chroot}!" -e "s!@CONFDIR@!${confdir}!" -e "/^@/d" ${confdir}/syslog-ng.conf >> /etc/syslog-ng.conf
		    service_restart_syslog_ng=1
		fi
	    fi
	    ;;
	disable)
	    if grep -q "^# BEGIN: Automatically added by postfix chroot setup script for ${chroot}\$" /etc/syslog-ng.conf; then
		sed -i -e "\!^# BEGIN: Automatically added by postfix chroot setup script for ${chroot}\$!,\!^# END ${chroot}\$!d" /etc/syslog-ng.conf
		service_restart_syslog_ng=1
	    elif grep -q "^# BEGIN: Automatically added by postfix chroot setup script\$" /etc/syslog-ng.conf; then
		sed -i -e '/^# BEGIN: Automatically added by postfix chroot setup script$/,/^# END$/d' /etc/syslog-ng.conf
		service_restart_syslog_ng=1
	    fi
	    ;;
    esac
}
update_syslogng() {
# note: we use a single configuration file for all postfix instances, to avoid issue in case an instance is renamed
    case $1 in
	enable)
	    if ! grep -qs -E "(unix-stream|file)[[:space:]]*\([[:space:]]*([\"'])${chroot}/dev/log\2" /etc/syslog-ng.d/postfix_chroot.conf; then
		# we need to give a different name to each source
		local instance_name=`postconf -c ${confdir} -h multi_instance_name 2>/dev/null`
		echo "# BEGIN: Automatically added by postfix chroot setup script for ${chroot}" >> /etc/syslog-ng.d/postfix_chroot.conf
		echo "source s_postfix_chroot${instance_name:+_$instance_name} { unix-stream(\"${chroot}/dev/log\"); };" >> /etc/syslog-ng.d/postfix_chroot.conf
		echo "# END ${chroot}" >> /etc/syslog-ng.d/postfix_chroot.conf
		service_restart_syslog_ng=1
	    fi
	    ;;
	disable)
	    if grep -qs "^# BEGIN: Automatically added by postfix chroot setup script for ${chroot}\$" /etc/syslog-ng.d/postfix_chroot.conf; then
		sed -i -e "\!^# BEGIN: Automatically added by postfix chroot setup script for ${chroot}\$!,\!^# END ${chroot}\$!d" /etc/syslog-ng.d/postfix_chroot.conf
		[ -f /etc/syslog-ng.d/postfix_chroot.conf -a ! -s /etc/syslog-ng.d/postfix_chroot.conf ] && rm -f /etc/syslog-ng.d/postfix_chroot.conf
		service_restart_syslog_ng=1
	    fi
	    ;;
    esac
}
update_syslog() {
    case $1 in
	enable)
	    mkdir -p ${chroot}/dev 2>/dev/null
	    ;;
	disable)
	    rm -f ${chroot}/dev/log 2>/dev/null
	    rmdir ${chroot}/dev 2>/dev/null
	    ;;
    esac
    [ -f '/etc/sysconfig/syslog' ] && update_sysklogd $1
    [ -f '/etc/sysconfig/rsyslog' ] && update_rsyslog $1
    if [ -f '/etc/syslog-ng.conf' ]; then 
	if [ -d '/etc/syslog-ng.d' ]; then
	    update_syslogng_old disable # clean cruft if upgraded syslog-ng version
	    update_syslogng $1
	else
	    update_syslogng_old $1
	fi
    fi
}

##########################################################################
#
# remove chroot jail

remove_chroot () {
    verbose=1

    [ "$1" = "quiet" ] && verbose=0
    [ "$1" = "noconf" ] && verbose=0 && noconf=1

    info "removing chroot from: ${chroot}"

    # remove system files
    info "remove system files from chroot"
    for i in ${BASE_FILES} \
	    etc/passwd etc/group \
	    etc/samba/smb.conf etc/samba/lmhosts \
	    etc/ldap.conf ; do
	remove $i
    done

    info "remove additional files from chroot"
    for i in $ADDITIONAL_FILES; do
	# in case we have /path/file=/newpath/newfile
	remove ${i##*=}
    done

    info "removing chroot libraries from: ${chroot}"

    # remove nss libraries
    libs=""
    for l in ${chroot}/${_lib}/lib*.so* ${chroot}/usr/${_lib}/lib*.so*; do
	[ -f $l ] && \
	    libs="$libs $l `ldd $l | awk -v c=${chroot} '{print c $3}'`"
    done
    
    if [ -n "$libs" ]; then
	info "remove nss files from chroot"
	for l in $libs; do
	    remove $l
	done
    fi

    info "remove system directories from chroot"
    for dir in var/lib/sasl2 var/lib var usr/share/zoneinfo \
	usr/share usr/${_lib} usr ${_lib} etc; do
	[ -d ${chroot}/${dir} ] && \
	    info "  ${chroot}/${dir}" && \
	    rmtree ${chroot}/${dir}
    done

    [ "$noconf" = "1" ] && return
    
    # remove chroot settings from master.cf
    awk -v ALWAYS_CHROOT_PROGRAM="$ALWAYS_CHROOT_PROGRAM" \
	-v ALWAYS_CHROOT_SERVICE="$ALWAYS_CHROOT_SERVICE" '
	    BEGIN                   { IFS="[ \t]+"; OFS="\t"; }
	    /^#/                    { print; next; }
	    /^ /                    { print; next; }
	    $1 ~ ALWAYS_CHROOT_SERVICE    { print; next; }
	    $8 ~ ALWAYS_CHROOT_PROGRAM    { print; next; }
	    $5 == "y"               { $5="n"; print $0; next; }
				    { print; }
	' ${confdir}/master.cf.${bckext} > ${confdir}/master.cf
}

#
##########################################################################

##########################################################################
#
# setup chroot jail

setup_chroot () {
    verbose=1

    [ -n "$1" ] && [ "$1" = quiet ] && verbose=0

    # Check master.cf is where we expect it
    [ -f ${confdir}/master.cf ] || error "${confdir}/master.cf missing, exiting"
    info "setting up chroot at: ${chroot}"

    # copy system files into chroot environment
    info "copy system files into chroot"
    for i in ${BASE_FILES}; do
	[ -e ${i} ] && copy ${i}
    done

    info "copy additional files into chroot"
    for i in $ADDITIONAL_FILES; do
	# in case we have /path/file=/newpath/newfile
	copy ${i%%=*} ${i##*=}
    done

    # for sasl
    mkdir -p ${chroot}/var/lib/sasl2 2>/dev/null

    # for ldaps
    mkdir -p ${chroot}/dev
    cp -af /dev/urandom ${chroot}/dev

    # check smtpd's dependencies to determine which libraries
    # don't need to be copied into the chroot

    smtpd=`${postconf} -c ${confdir} -h daemon_directory`/smtpd
    if [ ! -x "${smtpd}" ];then
	warn "cannot find \$daemon_directory/smtpd"
    fi

    # check also dynamic maps dependencies
    [ -s ${confdir}/dynamicmaps.cf ] && \
	dynmaps=`awk '/^[[:space:]]*#/ {next} {print $2}' ${confdir}/dynamicmaps.cf`

    prunedeps="none"
    for i in ${smtpd} ${dynmaps}; do
	prunedeps=`echo $prunedeps;/usr/bin/ldd $i | awk '/\// {print $(NF-1)}'`
    done

    nss_libs=
    for i in ${nss_databases}; do
        nss=`[ -s /etc/nsswitch.conf ] && \
	    awk -v db=$i: -v IGNORE_NSS_LIBS="${IGNORE_NSS_LIBS}" '
	    /^[[:space:]]*#/ {next}
	    $1 == db {
		for (i=2;i<=NF;i++) {
		    if (match($i,"#")) {next}
		    if (!match($i,"=") && !match($i,IGNORE_NSS_LIBS)) {print $i}
		}
	    } ' /etc/nsswitch.conf`
	[ -z "$nss" ] && eval `echo nss=\\\$nss_default_$i`
	nss_libs="$nss_libs $nss"
    done

    libs=
    for i in ${nss_libs}; do
	case $i in
	    wins) conf="/etc/samba/smb.conf /etc/samba/lmhosts" ;;
	    ldap) conf="/etc/ldap.conf" ;; # i purposefully ignore copying of /etc/ldap.secret
	    *) conf="" ;;
	esac
	l=/${_lib}/libnss_$i.$nss_soname
	[ -e ${l} -a "${libs##*$l*}" == "${libs}" ] && \
	    libs=`echo $conf; echo $l;echo $libs;/usr/bin/ldd $l | awk '/\// {print $(NF-1)}'`
    done

    #now copy nss libraries and dependencies if we don't already have them loaded
    info "copy nss libraries into chroot"
    for i in $libs; do
	[ -n "${prunedeps##*$i*}" ] && copy ${i}
    done

    # chroot master.cf change all lines except pipe, local, proxymap,
    # virtual and spawn
    awk -v NEVER_CHROOT_PROGRAM="$NEVER_CHROOT_PROGRAM" \
	-v NEVER_CHROOT_SERVICE="$NEVER_CHROOT_SERVICE" '
	    BEGIN                   { IFS="[ \t]+"; OFS="\t"; }
	    /^#/                    { print; next; }
	    /^ /                    { print; next; }
	    $1 ~ NEVER_CHROOT_SERVICE    { print; next; }
	    $8 ~ NEVER_CHROOT_PROGRAM    { print; next; }
	    $5 == "n"               { $5="y"; print $0; next; }
				    { print; }
	' ${confdir}/master.cf.${bckext} > ${confdir}/master.cf
}

#
##########################################################################

##########################################################################
#
# check files in chroot

check_files() {
    local i j f rc
    rc=0
    for i in ${BASE_FILES} ${ADDITIONAL_FILES}; do
	f=${i%%=*}
	f=${f#/}
	i=${i##*=}
	i=${i#/}
	if [ -f /${i} -a ! -f ${chroot%/}/${f} ]; then
	    info "file ${chroot%/}/${i} missing"
	    rc=1
	fi
    done
    cd $chroot || return 1
    for i in `find bin etc lib sbin usr -type f -print 2>/dev/null`; do
	f=$i
	for j in ${ADDITIONAL_FILES}; do
	    [ "$i" = "${j%%=*}" ] && f=${i##*=}
	done
	if [ -f /$f ]; then
	    cmp -s $i /$f || {
		info "files ${chroot%/}/${i} and /${f#/} differ"
		rc=1
	    }
	fi
    done

    if [ ! -d  ${chroot%/}/var/lib/sasl2 ]; then
	    info "directory ${chroot%/}/var/lib/sasl2 missing"
	    rc=1
    fi

    if [ ! -c  ${chroot%/}/dev/urandom ]; then
	    info "device file ${chroot%/}/dev/urandom missing"
	    rc=1
    fi

    return $rc
}

#
##########################################################################

##########################################################################
#
# create/update /etc/sysconfig/postfix

create_sysconfig() {
    cat > /etc/sysconfig/postfix <<-EOF
	# this file is automatically generated by postfix-chroot.sh
	# you can modify the parameters and they will be mantained
	# comments will not be preserved

	# use postfix-chroot.sh to change this
	CHROOT=${CHROOT}
	# this are regular expressions matching a whole line
	NEVER_CHROOT_PROGRAM='${NEVER_CHROOT_PROGRAM}'
	ALWAYS_CHROOT_PROGRAM='${ALWAYS_CHROOT_PROGRAM}'
	NEVER_CHROOT_SERVICE='${NEVER_CHROOT_SERVICE}'
	ALWAYS_CHROOT_SERVICE='${ALWAYS_CHROOT_SERVICE}'
	# nss names as they would appear in nsswitch.conf
	IGNORE_NSS_LIBS='${IGNORE_NSS_LIBS}'
	# space separated list of full pathname of file you want to be copied
	# use /path/file=/newpath/newfile for path mappings
	ADDITIONAL_FILES='${ADDITIONAL_FILES}'
	# Automatically rebuild maps at daemon startup
	REBUILD_ALIASES=${REBUILD_ALIASES}
	REBUILD_MAPS=${REBUILD_MAPS}
	# Multi instance support in initscripts and chroot. If disabled only
	# default instance will be started/stopped automatically
	MANAGE_MULTI_INSTANCES=${MANAGE_MULTI_INSTANCES}
	# The following two variables are used to limit the instances (or
	# groups of) that are started/stopped automatically. Put space
	# separated lists of instance or group _names_ there.
	MANAGE_ONLY_INSTANCES='${MANAGE_ONLY_INSTANCES}'
	MANAGE_ONLY_INSTANCE_GROUPS='${MANAGE_ONLY_INSTANCE_GROUPS}'
	# Space separated list of instance configuration _directories_
	# that will not be chrooted
	DONT_CHROOT_INSTANCES='${DONT_CHROOT_INSTANCES}'

EOF
}

#
##########################################################################


default_config_directory=/etc/postfix
verbose=1
[ "$1" = "-q" ] && { quiet=quiet; verbose=0; shift; }
[ "$1" = "-h" ] && { usage; exit 0; }

[ -z "$1" -o -n "$3" ] && { usage; exit 1; }

if [ -n "$2" ]; then
    config_directory="$2"
else
    config_directory=${default_config_directory}
fi

[ "$UID" = "0" ] || error "your must be root to run this script"

_lib=`rpm --eval '%_lib'`
postconf=/usr/sbin/postconf
[ -x ${postconf} ] || error "can not find postconf"
[ -d "${config_directory}" -a -s "${config_directory}/main.cf" -a -s "${config_directory}/master.cf" ] || error "${config_directory} is not a postfix configuration directory"

if [ "${config_directory}" == "${default_config_directory}" -a "`postconf -c ${config_directory} -h multi_instance_enable 2>/dev/null`" = "yes" ]; then
    multi_instance_directories=`postconf -c ${config_directory} -h multi_instance_directories 2>/dev/null`
fi

# defaults
CHROOT=0
NEVER_CHROOT_PROGRAM='^(proxymap|local|pipe|virtual|spawn)$'
NEVER_CHROOT_SERVICE='^cyrus$'
ALWAYS_CHROOT_PROGRAM='^$'
ALWAYS_CHROOT_SERVICE='^$'
IGNORE_NSS_LIBS='^(mdns.*|ldap|db|wins)$'
ADDITIONAL_FILES=''
REBUILD_ALIASES=1
REBUILD_MAPS=1
MANAGE_MULTI_INSTANCES=1
MANAGE_ONLY_INSTANCES=''
MANAGE_ONLY_INSTANCE_GROUPS=''
DONT_CHROOT_INSTANCES=''
[ -s /etc/sysconfig/postfix ] && . /etc/sysconfig/postfix

BASE_FILES='/etc/localtime /etc/host.conf /etc/resolv.conf /etc/nsswitch.conf /etc/hosts /etc/services'

# defaults for NSS
# do i really need to look at passwd and group?
nss_databases='passwd group hosts services'
nss_default_passwd="compat"
nss_default_group="compat"
nss_default_hosts="dns files"
nss_default_services="nis files"
nss_soname=so.2

bckext=`date '+%Y%m%d-%H%M'`

get_chroot() {
    local dir
    for dir in ${DONT_CHROOT_INSTANCES}; do
	[ "${confdir}" == "${dir}" ] && return
    done
    if [ "${config_directory}" != "${confdir}" -a "`postconf -c ${confdir} -h multi_instance_enable 2>/dev/null`" != "yes" ]; then
	info "skipping disabled instance ${confdir}"
	return
    fi
	
    local chroot=`${postconf} -c ${confdir} -h queue_directory 2>/dev/null`
    if [ -z "${chroot}" ]; then
	warn "chroot (${chroot}) is not defined"
	return
    fi
    if [ "${chroot}" = "/" ]; then
	warn "chroot (${chroot}) is set to /"
	return
    fi
    if [ ! -d "${chroot}" ]; then
	warn "chroot (${chroot}) is not a directory"
	return
    fi
    echo ${chroot}
}

enable_chroot() {
    for confdir in ${config_directory} ${multi_instance_directories}; do
	chroot=`get_chroot`
	[ -z "${chroot}" ] && continue

	cp -p ${confdir}/master.cf ${confdir}/master.cf.${bckext}
	remove_chroot noconf
	setup_chroot $quiet
	cmp -s ${confdir}/master.cf ${confdir}/master.cf.${bckext} && rm -f ${confdir}/master.cf.${bckext}
	[ -f ${confdir}/master.cf.${bckext} ] && info "${confdir}/master.cf backed up as ${confdir}/master.cf.${bckext}"
	update_syslog enable
    done
}

disable_chroot() {
    for confdir in ${config_directory} ${multi_instance_directories}; do
	chroot=`get_chroot`
	[ -z "${chroot}" ] && continue

	update_syslog disable
	cp -p ${confdir}/master.cf ${confdir}/master.cf.${bckext}
        remove_chroot ${1}
	cmp -s ${confdir}/master.cf ${confdir}/master.cf.${bckext} && rm -f ${confdir}/master.cf.${bckext}
	[ -f ${confdir}/master.cf.${bckext} ] && info "${confdir}/master.cf backed up as ${confdir}/master.cf.${bckext}"
    done
}

delete_chroot() {
    for confdir in ${config_directory} ${multi_instance_directories}; do
	chroot=`get_chroot`
	[ -z "${chroot}" ] && continue

	cp -p ${confdir}/master.cf ${confdir}/master.cf.${bckext}
	update_syslog disable
	remove_chroot noconf
    done
}

check_chroot() {
    for confdir in ${config_directory} ${multi_instance_directories}; do
	chroot=`get_chroot`
	[ -z "${chroot}" ] && continue

	check_files
    done
}

update_chroot() {
    for confdir in ${config_directory} ${multi_instance_directories}; do
	chroot=`get_chroot`
	[ -z "${chroot}" ] && continue

	check_files && continue

	cp -p ${confdir}/master.cf ${confdir}/master.cf.${bckext}
	remove_chroot noconf
	setup_chroot $quiet
	cmp -s ${confdir}/master.cf ${confdir}/master.cf.${bckext} && rm -f ${confdir}/master.cf.${bckext}
	[ -f ${confdir}/master.cf.${bckext} ] && info "${confdir}/master.cf backed up as ${confdir}/master.cf.${bckext}"
	update_syslog enable
    done
}

# create readable directories into the chroot
umask 022

# See how we were called.
case "$1" in
    enable)
	CHROOT=1
	create_sysconfig
	enable_chroot
        ;;
    disable)
	CHROOT=0
	create_sysconfig
	disable_chroot $quiet
        ;;
    remove)
	# used by rpm preuninstall script
	delete_chroot
	_noreload=1
	;;
    update)
	if [ $CHROOT = 0 ];then
	    info "chroot disabled in /etc/sysconfig/postfix"
	    exit 0
	else
	    enable_chroot
	fi
	;;
    check)
	if [ $CHROOT = 0 ];then
	    info "chroot disabled in /etc/sysconfig/postfix"
	    exit 0
	else
	    check_chroot
	    _noreload=1
	fi
    ;;
    check_update)
	if [ $CHROOT = 0 ];then
	    info "chroot disabled in /etc/sysconfig/postfix"
	    exit 0
	else
	    update_chroot
	fi
    ;;
    create_sysconfig)
	create_sysconfig
	exit 0
    ;;
    *)
	usage
	exit 1
        ;;
esac

[ -n "${service_restart_syslog}" ] && service syslog condrestart
[ -n "${service_restart_rsyslog}" ] && service rsyslog condrestart
[ -n "${service_restart_syslog_ng}" ] && service syslog-ng condrestart
[ -z "${_noreload}" -a -f /var/lock/subsys/postfix ] && service postfix reload

exit 0

# vim:ts=8:sw=4
