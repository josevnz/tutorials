# Packaging software in multiple formats with FPM

![Mask made of bullets](mask_made_of_disposed_ammo.jpg)

[FPM](https://fpm.readthedocs.io/en/latest/getting-started.html) is a powerful wrapper that will allow you to create 
packages for multiple programs in multiple operating systems. In this tutorial I will 
show you how you can replace some tedious packaging of third party applications.

## What do you need to complete this tutorial

* A Linux distribution (I used Fedora but this works with anything)
* Elevated privileges (if you want to install your own packages)

## When my package manager is not simple enough

Many times we want to have the ultimate control how we package an application, but there are
a few occasions when this may be overkill:

1. The third party application is simple or small enough than a tar would be good enough to install it. Yet you want to enjoy the benefits of upgrades and roll-back, like the ones offered by RPM.
2. You need or want to package an application from one format (say .tar.gz) to Debian '.deb' or RPM.
3. You have to package multiple applications that are only offered in Source format or pre-packaged binaries, like when upgrading the operating system. And you don't want to spend an eternity re-packaging the third party applications.

## Packaging an existing application, jdumpertools, the old way

I don't want to repeat myself, I wrote [a different tutorial that explains in detail](https://github.com/josevnz/tutorials/blob/main/docs/Packaging_your_software_using_RPM.md) how you can make an
RPM for an existing application. 

As you can see, there are a few manual steps required to create the RPM:

1. Download the source distribution (or binary)
2. Prepare the [RPM spec file](https://github.com/josevnz/jdumpertools/blob/main/jdumpertools.spec), which should take care of compilation (or just packaging) of the software, as well the location for the instalation
3. Lint the spec file, fix common errors

So let's see how this project, [jdumpertools](ttps://github.com/josevnz/jdumpertools), RPM spec file works:

First take a look at the spec file:

```ini
Name:           jdumpertools
# TODO: Figure out a better way to update version here and on Makefile
%global major 0
Version:        v%{major}.2
Release:        1%{?dist}
Summary:        Programs that can be used to dump Linux usage data in JSON format

License:        ASL 2.0
URL:            https://github.com/josevnz/jdumpertools
Source0:        %{name}-%{version}.tar.gz

BuildRequires:  bash,tar,gzip,rpmdevtools,rpmlint,make,gcc >= 10.2.1
Requires:       bash

%global debug_package %{nil}

%description

Jdumpertools is a collection of programs that can be used to dump
linux usage data in JSON format, so it can be ingested by other tools.

* jdu: Similar to UNIX '/bin/du' command.
* jutmp: UTMP database dumper

%prep
%setup -q -n jdumpertools

%build
make all

%install

/usr/bin/mkdir -p %{buildroot}/%{_bindir}
/usr/bin/mkdir -p %{buildroot}/%{_mandir}/man8
/usr/bin/cp -v -p jdu jutmp %{buildroot}/%{_bindir}
/usr/bin/cp -v -p jdu.1 jutmp.1 %{buildroot}/%{_mandir}/man8/
/usr/bin/gzip %{buildroot}/%{_mandir}/man8/*
/usr/bin/mkdir -p %{buildroot}/%{_libdir}
/usr/bin/cp -v -p libjdumpertools.so.%{major} %{buildroot}/%{_libdir}
/usr/bin/strip %{buildroot}/%{_bindir}/{jdu,jutmp}
/usr/bin/strip %{buildroot}/%{_libdir}/*

%clean
rm -rf %{buildroot}

%files
%{_bindir}/jdu
%{_bindir}/jutmp
%{_libdir}/libjdumpertools.so.%{major}
%{_libdir}/libjdumpertools.so
%license LICENSE
%doc README.md
%doc %{_mandir}/man8/jdu.1.gz
%doc %{_mandir}/man8/jutmp.1.gz


%changelog
* Sun Oct  3 2021 Jose Vicente Nunez <kodegeek.com@protonmail.com> - v0.2-1
- Applied fixes from rpmlint: man page, typos on spec file, striped binaries, etc.
* Mon Jan  4 2021 Jose Vicente Nunez <kodegeek.com@protonmail.com> - v0.1-1
- First version being packaged
```

And now let's build it

```shell
[josevnz@dmaf5 jdumpertools]$ sudo dnf install -y rpmdevtools rpmlint
...
[josevnz@dmaf5 test]$ git clone https://github.com/josevnz/jdumpertools.git
Cloning into 'jdumpertools'...
remote: Enumerating objects: 228, done.
remote: Counting objects: 100% (228/228), done.
remote: Compressing objects: 100% (137/137), done.
remote: Total 228 (delta 132), reused 157 (delta 79), pack-reused 0
Receiving objects: 100% (228/228), 3.15 MiB | 9.67 MiB/s, done.
Resolving deltas: 100% (132/132), done.

[josevnz@dmaf5 test]$ cd jdumpertools/
[josevnz@dmaf5 jdumpertools]$ rpmbuild -ba jdumpertools.spec
...
+ exit 0
Provides: jdumpertools = v0.2-1.fc37 jdumpertools(x86-64) = v0.2-1.fc37 libjdumpertools.so()(64bit)
Requires(rpmlib): rpmlib(CompressedFileNames) <= 3.0.4-1 rpmlib(FileDigests) <= 4.6.0-1 rpmlib(PayloadFilesHavePrefix) <= 4.0-1
Requires: libc.so.6()(64bit) libc.so.6(GLIBC_2.2.5)(64bit) libc.so.6(GLIBC_2.3)(64bit) libjdumpertools.so()(64bit) rtld(GNU_HASH)
Checking for unpackaged file(s): /usr/lib/rpm/check-files /home/josevnz/rpmbuild/BUILDROOT/jdumpertools-v0.2-1.fc37.x86_64
Wrote: /home/josevnz/rpmbuild/SRPMS/jdumpertools-v0.2-1.fc37.src.rpm
Wrote: /home/josevnz/rpmbuild/RPMS/x86_64/jdumpertools-v0.2-1.fc37.x86_64.rpm
Executing(%clean): /bin/sh -e /var/tmp/rpm-tmp.42keBq
+ umask 022
+ cd /home/josevnz/rpmbuild/BUILD
+ cd jdumpertools
+ rm -rf /home/josevnz/rpmbuild/BUILDROOT/jdumpertools-v0.2-1.fc37.x86_64
+ RPM_EC=0
++ jobs -p
+ exit 0
Executing(rmbuild): /bin/sh -e /var/tmp/rpm-tmp.aZjb6s
+ umask 022
+ cd /home/josevnz/rpmbuild/BUILD
+ rm -rf jdumpertools jdumpertools.gemspec
+ RPM_EC=0
++ jobs -p
+ exit 0
...
[josevnz@dmaf5 jdumpertools]$ ls -l $HOME/rpmbuild/RPMS/x86_64/jdumpertools-v0.2-1.fc37.x86_64.rpm
-rw-r--r--. 1 josevnz josevnz 22118 Jun  2 14:03 /home/josevnz/rpmbuild/RPMS/x86_64/jdumpertools-v0.2-1.fc37.x86_64.rpm
```

Then you install the RPM like any other RPM:

```shell
[josevnz@dmaf5 jdumpertools]$ sudo dnf install -y $HOME/rpmbuild/RPMS/x86_64/jdumpertools-v0.2-1.fc37.x86_64.rpm
Last metadata expiration check: 1:36:46 ago on Fri 02 Jun 2023 12:30:31 PM EDT.
Dependencies resolved.
=================================================================================================================================
 Package                         Architecture              Version                         Repository                       Size
=================================================================================================================================
Installing:
 jdumpertools                    x86_64                    v0.2-1.fc37                     @commandline                     22 k

Transaction Summary
=================================================================================================================================
Install  1 Package

Total size: 22 k
Installed size: 57 k
Downloading Packages:
Running transaction check
Transaction check succeeded.
Running transaction test
Transaction test succeeded.
Running transaction
  Preparing        :                                                                                                         1/1 
  Installing       : jdumpertools-v0.2-1.fc37.x86_64                                                                         1/1 
  Running scriptlet: jdumpertools-v0.2-1.fc37.x86_64                                                                         1/1 
  Verifying        : jdumpertools-v0.2-1.fc37.x86_64                                                                         1/1 

Installed:
  jdumpertools-v0.2-1.fc37.x86_64                                                                                                

Complete!
```

It is not terrible, specially if you plan to make updates but can we do this _easier_?

## Installing FPM

The [getting started](https://fpm.readthedocs.io/en/latest/getting-started.html) document the simplest reference you need.

First some dependencies, for example in Fedora
```shell
[josevnz@dmaf5 jdumpertools]$ sudo dnf install -y gem
[josevnz@dmaf5 jdumpertools]$ sudo dnf install -y rpm-build squashfs-tools
```

And then fpm itself:
```shell
[josevnz@dmaf5 jdumpertools]$ gem install --user-install fpm
Fetching insist-1.0.0.gem
Fetching clamp-1.0.1.gem
Fetching stud-0.0.23.gem
Fetching rexml-3.2.5.gem
Fetching mustache-0.99.8.gem
Fetching dotenv-2.8.1.gem
Fetching cabin-0.9.0.gem
Fetching pleaserun-0.0.32.gem
Fetching fpm-1.15.1.gem
Fetching backports-3.24.1.gem
...
Done installing documentation for stud, rexml, mustache, insist, dotenv, clamp, cabin, pleaserun, backports, arr-pm, fpm after 5 seconds
11 gems installed
```

## Doing it again: Packaging jdumpertools as an RPM, without a spec file

Well, we need some files to package. This distribution comes with a Makefile, so easy as pie we do:

```shell
[josevnz@dmaf5 jdumpertools]$ make
gcc -Wall -g -Og -Wextra -Werror -Werror=format-security -std=c11   -DJDUMPERTOOLS_VERSION=v0.2 -fPIC jdumpertools.h jdumpertools.c -I /home/josevnz/test/jdumpertools -shared -Wl,-soname,libjdumpertools.so -o libjdumpertools.so.0
gcc jdumpertools.h jdu.c libjdumpertools.so.0 -Wall -g -Og -Wextra -Werror -Werror=format-security -std=c11   -DJDUMPERTOOLS_VERSION=v0.2 -L /home/josevnz/test/jdumpertools -l jdumpertools -o jdu
gcc jdumpertools.h jutmp.c -Wall -g -Og -Wextra -Werror -Werror=format-security -std=c11   -DJDUMPERTOOLS_VERSION=v0.2 -L /home/josevnz/test/jdumpertools -l jdumpertools -o jutmp
...
[josevnz@dmaf5 jdumpertools]$ ls
CODE_OF_CONDUCT.md  INSTALL.md  jdu.c           jdumpertools.spec  jutmp.c               Makefile        SECURITY.md
CONTRIBUTING.md     jdu         jdumpertools.c  jutmp              libjdumpertools.so.0  mazinger-z.png
Dockerfile          jdu.1       jdumpertools.h  jutmp.1            LICENSE               README.md
[josevnz@dmaf5 jdumpertools]$ fpm -t rpm -s dir --name jdumpertools --rpm-autoreq --rpm-os linux --rpm-summary 'Programs that can be used to dump Linux usage data in JSON format' --license 'ASL 2.0' --version v0.21 --depends bash --maintainer 'Jose Vicente Nunez <kodegeek.com@protonmail.com>' --url https://github.com/josevnz/jdumpertools jdu=/usr/bin/jdu jutmp=/usr/bin/jutmp jdu.1=/usr/share/man/man1/jdu.1.gz jutmp.1=/usr/share/man/man8/jutmp.1.gz
Created package {:path=>"jdumpertools-v0.21-1.x86_64.rpm"}
```

So no spec file, and we got ourselves an RPM.

What if I want to create packages for other distributions? just a few changes on the command line:

_Debian package_:
```shell
[josevnz@dmaf5 jdumpertools]$ fpm -t deb -s dir --name jdumpertools --rpm-autoreq --rpm-os linux --rpm-summary 'Programs that can be used to dump Linux usage data in JSON format' --license 'ASL 2.0' --version v0.21 --depends bash --maintainer 'Jose Vicente Nunez <kodegeek.com@protonmail.com>' --url https://github.com/josevnz/jdumpertools jdu=/usr/bin/jdu jutmp=/usr/bin/jutmp jdu.1=/usr/share/man/man1/jdu.1.gz jutmp.1=/usr/share/man/man8/jutmp.1.gz
Debian 'Version' field needs to start with a digit. I was provided 'v0.21' which seems like it just has a 'v' prefix to an otherwise-valid Debian version, I'll remove the 'v' for you. {:level=>:warn}
Created package {:path=>"jdumpertools_0.21_amd64.deb"}
```

_Self extracting_ script:
```shell
[josevnz@dmaf5 jdumpertools]$ fpm -t sh -s dir --name jdumpertools --rpm-autoreq --rpm-os linux --rpm-summary 'Programs that can be used to dump Linux usage data in JSON format' --license 'ASL 2.0' --version v0.21 --depends bash --maintainer 'Jose Vicente Nunez <kodegeek.com@protonmail.com>' --url https://github.com/josevnz/jdumpertools jdu=/usr/bin/jdu jutmp=/usr/bin/jutmp jdu.1=/usr/share/man/man1/jdu.1.gz jutmp.1=/usr/share/man/man8/jutmp.1.gz
Created package {:path=>"jdumpertools.sh"}
```

_tar_ file:
```shell
[josevnz@dmaf5 jdumpertools]$ fpm -t tar -s dir --name jdumpertools --rpm-autoreq --rpm-os linux --rpm-summary 'Programs that can be used to dump Linux usage data in JSON format' --license 'ASL 2.0' --version v0.21 --depends bash --maintainer 'Jose Vicente Nunez <kodegeek.com@protonmail.com>' --url https://github.com/josevnz/jdumpertools jdu=/usr/bin/jdu jutmp=/usr/bin/jutmp jdu.1=/usr/share/man/man1/jdu.1.gz jutmp.1=/usr/share/man/man8/jutmp.1.gz
Created package {:path=>"jdumpertools.tar"}
```

This is already very convenient. Now I want to show you another use case for FPM

## Re-packaging existing software

Say that you want to distribute a CPAN module which doesn't have an RPM. You could spend quality time, or you can use FPM to do the work for you.

First, let's install a new dependency for Fedora:

```shell
[josevnz@dmaf5 jdumpertools]$ sudo dnf install -y perl-App-cpanminus
```

And then let's build our RPM
```shell
[josevnz@dmaf5 jdumpertools]$ fpm -t rpm -s cpan Archive::Tar
Created package {:path=>"perl-Archive-Tar-3.02-1.noarch.rpm"}
```
Did it work?

```shell
[josevnz@dmaf5 jdumpertools]$ rpm -qil perl-Archive-Tar-3.02-1.noarch.rpm
Name        : perl-Archive-Tar
Version     : 3.02
Release     : 1
Architecture: noarch
Install Date: (not installed)
Group       : default
Size        : 177677
License     : perl_5
Signature   : (none)
Source RPM  : perl-Archive-Tar-3.02-1.src.rpm
Build Date  : Fri 02 Jun 2023 04:36:45 PM EDT
Build Host  : dmaf5
Relocations : / 
Packager    : <josevnz@dmaf5>
Vendor      : Jos Boumans <kane[at]cpan.org>
URL         : http://example.com/no-uri-given
Summary     : Manipulates TAR archives
Description :
Manipulates TAR archives
/usr/local/bin/ptar
/usr/local/bin/ptardiff
/usr/local/bin/ptargrep
/usr/local/share/man/man1/ptar.1
/usr/local/share/man/man1/ptardiff.1
/usr/local/share/man/man1/ptargrep.1
/usr/local/share/man/man3/Archive::Tar.3pm
/usr/local/share/man/man3/Archive::Tar::File.3pm
/usr/local/share/perl5/5.36/Archive/Tar.pm
/usr/local/share/perl5/5.36/Archive/Tar/Constant.pm
/usr/local/share/perl5/5.36/Archive/Tar/File.pm
```

Going to show you how to package the [clickhouse-driver](https://clickhouse-driver.readthedocs.io/en/latest/installation.html#installation-from-pypi) module from PyPi.

```shell
[josevnz@dmaf5 jdumpertools]$ fpm -t rpm -s python 'clickhouse-driver'
Created package {:path=>"python-clickhouse-driver-0.2.6-1.x86_64.rpm"}
```

Say that now you want to create an RPM for OpenJDK 17. No problem, get the tar file and package it with a little help:

```shell
[josevnz@dmaf5 jdumpertools]$ curl --fail --location --remote-name https://github.com/adoptium/temurin17-binaries/releases/download/jdk-17.0.7%2B7/OpenJDK17U-jdk_x64_linux_hotspot_17.0.7_7.tar.gz
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
  0     0    0     0    0     0      0      0 --:--:-- --:--:-- --:--:--     0
100  182M  100  182M    0     0  10.9M      0  0:00:16  0:00:16 --:--:-- 11.1M
[josevnz@dmaf5 jdumpertools]$ fpm -t rpm -s tar --url 'https://adoptium.net/' --description 'Eclipse Temurin is the name of the OpenJDK distribution from Adoptium' --version '17.0.7+7' --prefix /usr/local/openjdk OpenJDK17U-jdk_x64_linux_hotspot_17.0.7_7.tar.gz
[josevnz@dmaf5 jdumpertools]$ rpm -qil OpenJDK17U-jdk_x64_linux_hotspot_17-17.0.7+7-1.x86_64.rpm
Name        : OpenJDK17U-jdk_x64_linux_hotspot_17
Version     : 17.0.7+7
Release     : 1
Architecture: x86_64
Install Date: (not installed)
Group       : default
Size        : 329508762
License     : unknown
Signature   : (none)
Source RPM  : OpenJDK17U-jdk_x64_linux_hotspot_17-17.0.7+7-1.src.rpm
Build Date  : Fri 02 Jun 2023 05:05:05 PM EDT
Build Host  : dmaf5
Relocations : /usr/local/openjdk 
Packager    : <josevnz@dmaf5>
Vendor      : none
URL         : https://adoptium.net/
Summary     : Eclipse Temurin is the name of the OpenJDK distribution from Adoptium
Description :
Eclipse Temurin is the name of the OpenJDK distribution from Adoptium
/usr/local/openjdk/jdk-17.0.7+7/NOTICE
/usr/local/openjdk/jdk-17.0.7+7/bin/jar
/usr/local/openjdk/jdk-17.0.7+7/bin/jarsigner
/usr/local/openjdk/jdk-17.0.7+7/bin/java
...
```

## What is next?

* FPM has [many other usages](https://fpm.readthedocs.io/en/latest/cli-reference.html), including transforming existing packages.
* FPM also supports [configuration files](https://fpm.readthedocs.io/en/latest/getting-started.html). If you are using it often then you should next to it.
* You may also consider running it [from inside a container](https://fpm.readthedocs.io/en/latest/docker.html), to avoid installing dependencies.

