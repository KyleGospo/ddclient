%global cachedir %{_localstatedir}/cache/ddclient
%global rundir   %{_rundir}/ddclient

Summary:           Client to update dynamic DNS host entries
Name:              ddclient
Version:           10.{{{ git_dir_version }}}
Release:           10%{?dist}
License:           GPLv2+
URL:               https://ddclient.net/
VCS:               {{{ git_dir_vcs }}}
Source:            {{{ git_dir_pack }}}

BuildArch:         noarch

BuildRequires:     perl-generators
BuildRequires:     systemd
Requires(pre):     shadow-utils
Requires(post):    systemd
Requires(preun):   systemd
Requires(postun):  systemd

Requires:          perl(Data::Validate::IP)
Requires:          perl(Digest::SHA1)
Requires:          perl(IO::Socket::INET6)
Requires:          perl(IO::Socket::SSL)
Requires:          perl(JSON::PP)

# Old NetworkManager expects the dispatcher scripts in a different place
Conflicts:         NetworkManager < 1.20

%description
ddclient is a Perl client used to update dynamic DNS entries for accounts
on many different dynamic DNS services. Features include: Operating as a
daemon, manual and automatic updates, static and dynamic updates, optimized
updates for multiple addresses, MX, wildcards, abuse avoidance, retrying
the failed updates and sending update status to syslog and through e-mail.

%prep
{{{ git_dir_setup_macro }}}
# Move pid file location for running as non-root.
sed -e 's|/var/run/ddclient.pid|%{rundir}/%{name}.pid|' \
    -i ddclient.conf.in
# Send less mail by default, eg. not on every shutdown.
sed -e 's|^mail=|#mail=|' -i ddclient.conf.in
# Backwards compatibility from pre-3.6.6-1
sed -e 's|/etc/ddclient/|%{_sysconfdir}/|' -i %{name}.in
sed -e 's|@PACKAGE_VERSION@|10|' -i %{name}.in


%build
#nothing to do


%install
install -D -p -m 755 %{name}.in $RPM_BUILD_ROOT%{_sbindir}/%{name}
install -D -p -m 600 ddclient.conf.in \
    $RPM_BUILD_ROOT%{_sysconfdir}/%{name}/%{name}.conf
install -D -p -m 644 ddclient.rwtab \
    $RPM_BUILD_ROOT%{_sysconfdir}/rwtab.d/%{name}

install -D -p -m 644 ddclient.service \
    $RPM_BUILD_ROOT%{_unitdir}/%{name}.service
install -D -p -m 644 ddclient.sysconfig \
    $RPM_BUILD_ROOT%{_sysconfdir}/sysconfig/%{name}
install -D -p -m 755 ddclient.NetworkManager \
    $RPM_BUILD_ROOT%{_prefix}/lib/NetworkManager/dispatcher.d/50-%{name}
install -D -p -m 644 ddclient-tmpfiles.conf \
    $RPM_BUILD_ROOT%{_tmpfilesdir}/%{name}.conf

mkdir -p $RPM_BUILD_ROOT%{cachedir}
mkdir -p $RPM_BUILD_ROOT%{rundir}
touch $RPM_BUILD_ROOT%{cachedir}/%{name}.cache

# Correct permissions for later usage in %doc
chmod 644 sample-*


%pre
getent group %{name} > /dev/null || %{_sbindir}/groupadd -r %{name}
getent passwd %{name} > /dev/null || %{_sbindir}/useradd -r -g %{name} -d %{_localstatedir}/cache/%{name} -s /sbin/nologin -c "Dynamic DNS Client" %{name}
exit 0

%post
%systemd_post %{name}.service
if [ $1 == 1 ]; then
    mkdir -p %{rundir}
    chown %{name}:%{name} %{rundir}
fi

%preun
%systemd_preun %{name}.service

%postun
%systemd_postun_with_restart %{name}.service


%files
%license COPYING COPYRIGHT

%{_sbindir}/%{name}
%{_tmpfilesdir}/%{name}.conf
%{_unitdir}/%{name}.service

# sysconfdir
%config(noreplace) %{_sysconfdir}/rwtab.d/%{name}
%config(noreplace) %{_sysconfdir}/sysconfig/%{name}
%attr(600,%{name},%{name}) %config(noreplace) %{_sysconfdir}/%{name}/%{name}.conf
%{_prefix}/lib/NetworkManager/dispatcher.d/50-%{name}

# localstatedir
%attr(0700,%{name},%{name}) %dir %{cachedir}
%attr(0600,%{name},%{name}) %ghost %{cachedir}/%{name}.cache
%ghost %attr(0755,%{name},%{name}) %dir %{rundir}


%changelog
{{{ git_dir_changelog }}}
