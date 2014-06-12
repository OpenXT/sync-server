%include common.inc

Name: sync-server
Summary: XenClient Synchronizer XT server scripts
Source0: %{name}.tar.gz
BuildArch: noarch
Requires: sync-database = %{version}

%define desc WSGI server scripts for XenClient Synchronizer XT.

%include description.inc
%include python.inc
