Name:           minio
Version:        0.0.%{_subver}
Release:        1.el%{_rhel_version}
Vendor:         Minio, Inc.
Summary:        Cloud Storage Server.
License:        Apache v2.0
Group:          Applications/File
Source0:        minio
Source1:        minio-client
Source2:        minio.sysconfig
Source3:        minio.service
URL:            https://www.minio.io/
BuildRoot:      %(mktemp -ud %{_tmppath}/%{name}-%{version}-%{release}-XXXXXX)

%if 0%{?fedora} >= 14 || 0%{?rhel} >= 7
BuildRequires:  systemd-units
Requires:       systemd
%endif
Requires(pre): shadow-utils

%description
Minio is an object storage server released under Apache License v2.0.
It is compatible with Amazon S3 cloud storage service. It is best
suited for storing unstructured data such as photos, videos, log
files, backups and container / VM images. Size of an object can
range from a few KBs to a maximum of 5TB.

%prep
%setup -q -T -c

%install
pwd
ls -la
mkdir -p %{buildroot}/%{_bindir}
cp %{SOURCE0} %{buildroot}/%{_bindir}
cp %{SOURCE1} %{buildroot}/%{_bindir}
mkdir -p %{buildroot}/%{_sysconfdir}/sysconfig
cp %{SOURCE2} %{buildroot}/%{_sysconfdir}/sysconfig/minio
mkdir -p %{buildroot}/var/lib/minio
mkdir -p %{buildroot}/var/lib/minio/volume
mkdir -p %{buildroot}/var/lib/minio/config

%if 0%{?fedora} >= 14 || 0%{?rhel} >= 7
mkdir -p %{buildroot}/%{_unitdir}
cp %{SOURCE3} %{buildroot}/%{_unitdir}/
%endif

%pre
getent group minio >/dev/null || groupadd -r minio
getent passwd minio >/dev/null || \
    useradd -r -g minio -d /var/lib/minio -s /sbin/nologin \
    -c "minio.io user" minio
exit 0

%if 0%{?fedora} >= 14 || 0%{?rhel} >= 7
%post
%systemd_post minio.service

%preun
%systemd_preun minio.service
%endif

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root,-)
%attr(755, root, root) %{_bindir}/minio
%attr(755, root, root) %{_bindir}/minio-client
%dir %attr(755, minio, minio) /var/lib/minio
%dir %attr(755, minio, minio) /var/lib/minio/volume
%dir %attr(755, minio, minio) /var/lib/minio/config
%config(noreplace) %{_sysconfdir}/sysconfig/minio

%if 0%{?fedora} >= 14 || 0%{?rhel} >= 7
%{_unitdir}/minio.service
%endif

%doc
