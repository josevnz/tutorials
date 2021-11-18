# Packaging applications your software using RPM

If you use RedHat or Fedora you will quickly find out yourself using 'dnf' (or yum) to install software packages. RPM is the most important software management tool on this Linux distributions and you will see shortly how you can take advantage of this framework to distribute your own software.

Hopefully you got a chance to read a previously written article on the [same subject](https://www.redhat.com/sysadmin/create-rpm-package) by Valentin Bajrami. I will repeat some of the same concepts here but will ilustrate a few issues you may find on the way when you package. Also will use a 2 more complex examples and a few issues you may find when packaging native applications.

By the end of this article you will be able to do:

* Determine how to compile and package your own native application for distribution
* Package third party applications that do not haven an RPM or maybe they do but you want to customize it.


I assume the following:

* You have basic knowledge of how to use RPM ([query packages](https://docs.fedoraproject.org/en-US/Fedora_Draft_Documentation/0.1/html/RPM_Guide/RPM_Guide-Using_RPM_DB-getting_information.html), [install, delete](https://docs.fedoraproject.org/en-US/Fedora_Draft_Documentation/0.1/html/RPM_Guide/ch-command-reference.html#id741230)). If that is not the case you can get familiar first with these concepts first and the come back here for some fun.
* You have Make, git, gcc and Java installed if you want to do complete *my exercices*. Not required but would be nice if you practice as we move along:

```shell=
sudo dnf install -y make gcc-10 java-11-openjdk-headless git
```

This will install make, gcc, java 11 and git using [dnf](https://dnf.readthedocs.io/en/latest/command_ref.html) package manager.


## Packaging your very own software using RPM

For this will use a small Open Source project called [jdumpertools](https://github.com/josevnz/jdumpertools).

On your Linux terminal, clone it and then compile it (you have installed Make and the gcc compiler, right? :-D)

```shell=
git clone git@github.com:josevnz/jdumpertools.git
cd jdumpertools
make all

josevnz@dmaf5 jdumpertools]$ ls -l jdu jutmp *.so
-rwxrwxr-x 1 josevnz josevnz 32728 Oct  3 16:40 jdu
-rwxrwxr-x 1 josevnz josevnz 32752 Oct  3 16:40 jutmp
-rwxrwxr-x 1 josevnz josevnz 29024 Oct  3 16:40 libjdumpertools.so

```

Then you can run any of the generated programs, for example JDU (a simpler version of the du command that prints the results in JSON format):
```shell=
[josevnz@dmaf5 jdumpertools]$ LD_LIBRARY_PATH=$PWD $PWD/jdu /
[{"partition": "/", "free_space": 462140129280.000000, "total_space": 510405902336.000000}]

```

So far so good. 

You will notice there is a file called [jdumpertools.spec](https://github.com/josevnz/jdumpertools/blob/main/jdumpertools.spec) on this directory. This is the RPM specification file that controls how to compile and package jdumpertools using RPM.

But before we move into building our RPM lets install a few supporting tools.

## Installing RPM building blocks

You will need the following
```shell=
sudo dnf install -y rpm-build rpmdevtools
```

Then we will prepare the sandbox to build your RPMS using our newly installed 'rpmdevtools'. You will never use root for that but your personal or developer Linux account (we will pass the -d debug flag):

```shell=
[josevnz@dmaf5 jdumpertools]$  /usr/bin/rpmdev-setuptree -d
josevnz       /home/josevnz    /home/josevnz/.rpmmacros
/home/josevnz/rpmbuild/RPMS    /home/josevnz/rpmbuild/SOURCES     /home/josevnz/rpmbuild/SPECS
/home/josevnz/rpmbuild/SRPMS   /home/josevnz/rpmbuild/BUILD

# A nicer view:

[josevnz@dmaf5 jdumpertools]$ tree ~/rpmbuild
/home/josevnz/rpmbuild
├── BUILD
├── RPMS
├── SOURCES
├── SPECS
└── SRPMS

5 directories, 0 files


```

Right now we only care about 2 directoties: SOURCES and SPECS. We will see the purpose of the rest in a bit.

Also a file called ~/.rpmmacros was created. You can put/ override some [special macros](https://docs.fedoraproject.org/en-US/packaging-guidelines/RPMMacros/) there to avoid repetitive tasks while buidilding your RPMS. This file is important because it 'anchors' your rpmbuild environment with your home directory.


## Packaging your application

We first will create a tar file of our source code in the ~/rpmbuild/SOURCES directory:

```shell=
VERSION=v0.1
NAME=jdumpertools
TARFILE=$(NAME)-$(VERSION).tar.gz
/usr/bin/tar --exclude-vcs --directory ../ --create --verbose --gzip --file $(HOME)/rpmbuild/SOURCES/$(TARFILE) $(NAME)
```

Normally the tar file contains scripts and source code we will compile as part of the packaging process.

Then we create a RPM spec file. 

Again, rpmdevtools gives you a head start like following:

```shell=
[josevnz@dmaf5 jdumpertools]$ rpmdev-newspec ~/rpmbuild/jose-package.spec
/home/josevnz/rpmbuild/jose-package.spec created; type minimal, rpm version >= 4.16.

[josevnz@dmaf5 jdumpertools]$ /bin/cat  ~/rpmbuild/jose-package.spec
Name:           jose-package
Version:        
Release:        1%{?dist}
Summary:        

License:        
URL:            
Source0:        

BuildRequires:  
Requires:       

%description

%prep
%autosetup

%build
%configure
%make_build

%install
rm -rf $RPM_BUILD_ROOT
%make_install


%files
%license add-license-file-here
%doc add-docs-here



%changelog
* Sun Oct 03 2021 Jose Vicente Nunez <josevnz@kodegeek.com>
- 
```

Don't worry if you cannot make sense of this file now, let's copy our jdumpertools.spec file to the ~/rpmbuild/SPECS directory:
```shell=
cp -p -v jdumpertools.spec ~/rpmbuild/SPECS
```

And create both a source and binary RPM:

```shell=
[josevnz@dmaf5 ~]$ rpmbuild -ba rpmbuild/SPECS/jdumpertools.spec
setting SOURCE_DATE_EPOCH=1609718400
Executing(%prep): /bin/sh -e /var/tmp/rpm-tmp.kBlIwO
+ umask 022
+ cd /home/josevnz/rpmbuild/BUILD
+ cd /home/josevnz/rpmbuild/BUILD
+ rm -rf jdumpertools
+ /usr/bin/gzip -dc /home/josevnz/rpmbuild/SOURCES/jdumpertools-v0.1.tar.gz
+ /usr/bin/tar -xof -
+ STATUS=0
+ '[' 0 -ne 0 ']'
+ cd jdumpertools
+ /usr/bin/chmod -Rf a+rX,u+w,g-w,o-w .
+ RPM_EC=0
++ jobs -p
+ exit 0
Executing(%build): /bin/sh -e /var/tmp/rpm-tmp.7qielL
+ umask 022
+ cd /home/josevnz/rpmbuild/BUILD
+ cd jdumpertools
+ make all
make: Nothing to be done for 'all'.
+ RPM_EC=0
++ jobs -p
+ exit 0
Executing(%install): /bin/sh -e /var/tmp/rpm-tmp.F6BrgN
+ umask 022
+ cd /home/josevnz/rpmbuild/BUILD
+ '[' /home/josevnz/rpmbuild/BUILDROOT/jdumpertools-v0.1-1.fc33.x86_64 '!=' / ']'
+ rm -rf /home/josevnz/rpmbuild/BUILDROOT/jdumpertools-v0.1-1.fc33.x86_64
++ dirname /home/josevnz/rpmbuild/BUILDROOT/jdumpertools-v0.1-1.fc33.x86_64
+ mkdir -p /home/josevnz/rpmbuild/BUILDROOT
+ mkdir /home/josevnz/rpmbuild/BUILDROOT/jdumpertools-v0.1-1.fc33.x86_64
+ cd jdumpertools
+ rm -rf /home/josevnz/rpmbuild/BUILDROOT/jdumpertools-v0.1-1.fc33.x86_64
+ /usr/bin/mkdir -p /home/josevnz/rpmbuild/BUILDROOT/jdumpertools-v0.1-1.fc33.x86_64//usr/bin
+ /usr/bin/cp -v -p jdu jutmp /home/josevnz/rpmbuild/BUILDROOT/jdumpertools-v0.1-1.fc33.x86_64//usr/bin
'jdu' -> '/home/josevnz/rpmbuild/BUILDROOT/jdumpertools-v0.1-1.fc33.x86_64//usr/bin/jdu'
'jutmp' -> '/home/josevnz/rpmbuild/BUILDROOT/jdumpertools-v0.1-1.fc33.x86_64//usr/bin/jutmp'
+ /usr/bin/mkdir -p /home/josevnz/rpmbuild/BUILDROOT/jdumpertools-v0.1-1.fc33.x86_64//usr/lib64
+ /usr/bin/cp -v -p libjdumpertools.so /home/josevnz/rpmbuild/BUILDROOT/jdumpertools-v0.1-1.fc33.x86_64//usr/lib64
'libjdumpertools.so' -> '/home/josevnz/rpmbuild/BUILDROOT/jdumpertools-v0.1-1.fc33.x86_64//usr/lib64/libjdumpertools.so'
+ '[' '%{buildarch}' = noarch ']'
+ QA_CHECK_RPATHS=1
+ case "${QA_CHECK_RPATHS:-}" in
+ /usr/lib/rpm/check-rpaths
+ /usr/lib/rpm/check-buildroot
+ /usr/lib/rpm/redhat/brp-ldconfig
+ /usr/lib/rpm/brp-compress
+ /usr/lib/rpm/brp-strip /usr/bin/strip
+ /usr/lib/rpm/brp-strip-comment-note /usr/bin/strip /usr/bin/objdump
+ /usr/lib/rpm/redhat/brp-strip-lto /usr/bin/strip
+ /usr/lib/rpm/brp-strip-static-archive /usr/bin/strip
+ /usr/lib/rpm/redhat/brp-python-bytecompile '' 1 0
+ /usr/lib/rpm/brp-python-hardlink
+ /usr/lib/rpm/redhat/brp-mangle-shebangs
Processing files: jdumpertools-v0.1-1.fc33.x86_64
Executing(%doc): /bin/sh -e /var/tmp/rpm-tmp.ToAGHO
+ umask 022
+ cd /home/josevnz/rpmbuild/BUILD
+ cd jdumpertools
+ DOCDIR=/home/josevnz/rpmbuild/BUILDROOT/jdumpertools-v0.1-1.fc33.x86_64/usr/share/doc/jdumpertools
+ export LC_ALL=C
+ LC_ALL=C
+ export DOCDIR
+ /usr/bin/mkdir -p /home/josevnz/rpmbuild/BUILDROOT/jdumpertools-v0.1-1.fc33.x86_64/usr/share/doc/jdumpertools
+ cp -pr README.md /home/josevnz/rpmbuild/BUILDROOT/jdumpertools-v0.1-1.fc33.x86_64/usr/share/doc/jdumpertools
+ RPM_EC=0
++ jobs -p
+ exit 0
Executing(%license): /bin/sh -e /var/tmp/rpm-tmp.swoM9N
+ umask 022
+ cd /home/josevnz/rpmbuild/BUILD
+ cd jdumpertools
+ LICENSEDIR=/home/josevnz/rpmbuild/BUILDROOT/jdumpertools-v0.1-1.fc33.x86_64/usr/share/licenses/jdumpertools
+ export LC_ALL=C
+ LC_ALL=C
+ export LICENSEDIR
+ /usr/bin/mkdir -p /home/josevnz/rpmbuild/BUILDROOT/jdumpertools-v0.1-1.fc33.x86_64/usr/share/licenses/jdumpertools
+ cp -pr LICENSE /home/josevnz/rpmbuild/BUILDROOT/jdumpertools-v0.1-1.fc33.x86_64/usr/share/licenses/jdumpertools
+ RPM_EC=0
++ jobs -p
+ exit 0
Provides: jdumpertools = v0.1-1.fc33 jdumpertools(x86-64) = v0.1-1.fc33 libjdumpertools.so()(64bit)
Requires(rpmlib): rpmlib(CompressedFileNames) <= 3.0.4-1 rpmlib(FileDigests) <= 4.6.0-1 rpmlib(PayloadFilesHavePrefix) <= 4.0-1
Requires: libc.so.6()(64bit) libc.so.6(GLIBC_2.2.5)(64bit) libc.so.6(GLIBC_2.3)(64bit) libjdumpertools.so()(64bit) rtld(GNU_HASH)
Checking for unpackaged file(s): /usr/lib/rpm/check-files /home/josevnz/rpmbuild/BUILDROOT/jdumpertools-v0.1-1.fc33.x86_64
Wrote: /home/josevnz/rpmbuild/SRPMS/jdumpertools-v0.1-1.fc33.src.rpm
Wrote: /home/josevnz/rpmbuild/RPMS/x86_64/jdumpertools-v0.1-1.fc33.x86_64.rpm
Executing(%clean): /bin/sh -e /var/tmp/rpm-tmp.uEyCyL
+ umask 022
+ cd /home/josevnz/rpmbuild/BUILD
+ cd jdumpertools
+ rm -rf /home/josevnz/rpmbuild/BUILDROOT/jdumpertools-v0.1-1.fc33.x86_64
+ RPM_EC=0
++ jobs -p
+ exit 0
```

The end result is 2 files, [a source RPM and a binary RPM](https://docs.fedoraproject.org/ro/Fedora_Draft_Documentation/0.1/html/RPM_Guide/ch11s03.html).

```shell=
Wrote: /home/josevnz/rpmbuild/SRPMS/jdumpertools-v0.1-1.fc33.src.rpm
Wrote: /home/josevnz/rpmbuild/RPMS/x86_64/jdumpertools-v0.1-1.fc33.x86_64.rpm

```

So what happens when you install each one of these RPMS?
1. If you install the source RPM, it will create the tar file and the spec file in your rpmbuild directory. This will allow you to recompile the application, make fixes to the RPM spec file, etc.
```shell=
[josevnz@dmaf5 ~]$ ls rpmbuild/{SPECS,SOURCES}
rpmbuild/SOURCES:
jdumpertools-v0.1.tar.gz

rpmbuild/SPECS:
jdumpertools.spec

```

2. If you install the binary RPM then you are doing the real thing: Installing the application: 
```shell=
[josevnz@dmaf5 ~]$ sudo rpm -ihv /home/josevnz/rpmbuild/RPMS/x86_64/jdumpertools-v0.1-1.fc33.x86_64.rpm
Verifying...                          ################################# [100%]
Preparing...                          ################################# [100%]
Updating / installing...
   1:jdumpertools-v0.1-1.fc33         ################################# [100%]
```

Quickly let's confirm installed RPMS is there:

```shell=
[josevnz@dmaf5 ~]$ rpm -qi jdumpertools
Name        : jdumpertools
Version     : v0.1
Release     : 1.fc33
Architecture: x86_64
Install Date: Sun 03 Oct 2021 06:32:50 PM EDT
Group       : Unspecified
Size        : 95002
License     : Apache License 2.0
Signature   : (none)
Source RPM  : jdumpertools-v0.1-1.fc33.src.rpm
Build Date  : Sun 03 Oct 2021 06:27:11 PM EDT
Build Host  : dmaf5.home
URL         : https://github.com/josevnz/jdumpertools
Summary     : Programs that can be used to dump Linux usage data in JSON format.
Description :

Jdumpertools is a collection of programs that can be used to dump linux usage data in JSON format, so it can be ingested by other tools.

* jdu: Similar to UNIX 'du' command.
* jutmp: UTMP database dumper

```

***Note**: Curious readers probably opened the Makefile and saw a target called 'rpm'*:

```
rpm: all
	test -x /usr/bin/rpmdev-setuptree && /usr/bin/rpmdev-setuptree|| /bin/mkdir -p -v ${HOME}/rpmbuild/{BUILD,RPMS,SOURCES,SPECS,SRPMS}
	/usr/bin/tar --exclude-vcs --directory ../ --create --verbose --gzip --file $(HOME)/rpmbuild/SOURCES/$(TARFILE) $(NAME)
	/usr/bin/rpmbuild -ba jdumpertools.spec

```

*This is a convenient shorcut to prepare your rpmbuild sandbox, tar your files after they got compiled with make and then package them using 'rpmbuild' command. Freel free to call and see what it happens. (```make rpm```)*


I showed you first *what commands and tools can be used to generate the RPM* files but now is time to show you *how to write* the RPM spec file...


## Creating a spec file for jdumper tools

[Working with spec files](https://rpm-packaging-guide.github.io/#working-with-spec-files) requires filling several metatada tags as well describing how you are going to compile/ package your application. Jdumpertools is a plain Ansi C application, so we unpack the sources, compile them, copy them into intermediate area (~/rpmbuild/BUILDROOT) and then package them for distribution.

Let's take a look at the [RPM spec file](https://github.com/josevnz/jdumpertools/blob/main/jdumpertools.spec):

```
Name:           jdumpertools
# TODO: Figure out a better way to update version here and on Makefile
Version:        v0.1        
Release:        1%{?dist}
Summary:        Programs that can be used to dump Linux usage data in JSON format. 

License:        Apache License 2.0
URL:            https://github.com/josevnz/jdumpertools
Source0:        %{name}-%{version}.tar.gz

BuildRequires:  bash,tar,gzip,rpmdevtools,rpmlint,make,gcc >= 10.2.1
Requires:       bash

%global debug_package %{nil}

%description

Jdumpertools is a collection of programs that can be used to dump linux usage data in JSON format, so it can be ingested by other tools.

* jdu: Similar to UNIX 'du' command.
* jutmp: UTMP database dumper

%prep
%setup -q -n jdumpertools

%build
make all

%install
rm -rf %{buildroot}
/usr/bin/mkdir -p %{buildroot}/%{_bindir}
/usr/bin/cp -v -p jdu jutmp %{buildroot}/%{_bindir}
/usr/bin/mkdir -p %{buildroot}/%{_libdir}
/usr/bin/cp -v -p libjdumpertools.so %{buildroot}/%{_libdir}

%clean
rm -rf %{buildroot}

%files
%{_bindir}/jdu
%{_bindir}/jutmp
%{_libdir}/libjdumpertools.so
%license LICENSE
%doc README.md


%changelog
* Mon Jan  4 2021 Jose Vicente Nunez <kodegeek.com@protonmail.com> - 0.1
- First version being packaged
```

So what is important here:
* Metadata like version, name and Source0. Note you can use variables or macros
* The unpack the sources in the %prep section, using the %setup macro (the RPM guide has plenty of details about the flags)
* BuildRequires: You must list what dependencies you need to build your package. These cannot be dynamically detected.
* %build section: We compile with make
* %install section: We copy what we need for our program to work (program, libraries)
* % Finally the files section where we can even specify if a file is a document (%doc), license file (%licence) or a regular file

Also important:
* I disabled the creation of debug code during packaging with ```%global debug_package %{nil}```
* The changelog is how you tell the world what changed with this new package version.

## Checking for errors in your spec file with rpmlint (finding the hard way that your RPM is not perfect)

It is always nice to check for obvious errors or ways to improve our RPMS:

```shell=
josevnz@dmaf5 jdumpertools]$ sudo dnf install -y rpmlint
```

So now let's check the RPM spec file:

```shell=
[josevnz@dmaf5 jdumpertools]$ rpmlint /home/josevnz/rpmbuild/SPECS/jdumpertools.spec 
/home/josevnz/rpmbuild/SPECS/jdumpertools.spec: W: invalid-url Source0: jdumpertools-v0.1.tar.gz
0 packages and 1 specfiles checked; 0 errors, 1 warnings.
```

[The rpmlint documentation](https://fedoraproject.org/wiki/Common_Rpmlint_issues) says than the **Source0** must be a well define URL (The value should be a valid, public HTTP, HTTPS, or FTP URL.). So will not worry about this warning:

What about the RPM itself?

```shell=
[josevnz@dmaf5 jdumpertools]$ make rpm
...
[josevnz@dmaf5 jdumpertools]$ rpmlint --info ~/rpmbuild/RPMS/x86_64/jdumpertools-v0.2-1.fc33.x86_64.rpm
jdumpertools.x86_64: W: summary-ended-with-dot C Programs that can be used to dump Linux usage data in JSON format.
jdumpertools.x86_64: W: spelling-error %description -l en_US du -> dew, doe, Du
jdumpertools.x86_64: E: description-line-too-long C Jdumpertools is a collection of programs that can be used to dump linux usage data in JSON format, so it can be ingested by other tools.
jdumpertools.x86_64: W: incoherent-version-in-changelog 0.1 ['v0.1-1.fc33', 'v0.1-1']
jdumpertools.x86_64: W: invalid-license Apache License 2.0
jdumpertools.x86_64: W: unstripped-binary-or-object /usr/bin/jdu
jdumpertools.x86_64: W: unstripped-binary-or-object /usr/bin/jutmp
jdumpertools.x86_64: W: unstripped-binary-or-object /usr/lib64/libjdumpertools.so
jdumpertools.x86_64: W: no-soname /usr/lib64/libjdumpertools.so
jdumpertools.x86_64: W: no-manual-page-for-binary jdu
jdumpertools.x86_64: W: no-manual-page-for-binary jutmp
1 packages and 0 specfiles checked; 1 errors, 10 warnings.

```

10 warnings and one error. Some are easy to fix:
* License must be on a specific [format](https://fedoraproject.org/wiki/Licensing:Main#License_of_Fedora_SPEC_Files).
* Man pages are required for programs: Yup, I wrote a very simple one with [troff](https://www.gnu.org/software/groff/) 
* Including the *[soname](https://ftp.gnu.org/old-gnu/Manuals/ld-2.9.1/html_node/ld_3.html)* in the library

After the fixes only 1 warning remains:
```shell=
[josevnz@dmaf5 jdumpertools]$ make rpm
...
[josevnz@dmaf5 jdumpertools]$ rpmlint --info ~/rpmbuild/RPMS/x86_64/jdumpertools-v0.2-1.fc33.x86_64.rpm 
jdumpertools.x86_64: W: spelling-error %description -l en_US du -> dew, doe, Du
The value of this tag appears to be misspelled. Please double-check.
```

We can ignore that one too.

Now we can upgrade our RPM with the improved version:

```shell=
sudo rpm -Uhv ~/rpmbuild/RPMS/x86_64/jdumpertools-v0.2-1.fc33.x86_64.rpm
```

## Packaging third party applications

Another very common scenario is the following: You found a piece of sfotware you want to use but there is no RPM for it.

For this example, I'm going to use a Java benchmark I like from NASA: [NAS Parallel Benchmarks](https://www.nas.nasa.gov/software/npb.html) (NPB3.0). I took their code and made a fork, adding only an improved build using [Gradle](https://gradle.org/).

### Step 1: Write a skeleton SPEC file

```shell
[josevnz@dmaf5 NPB3.0-JAV-FORK]$  /usr/bin/rpmdev-newspec --output ~/rpmbuild/SPECS/NPB.spec --type minimal
/home/josevnz/rpmbuild/SPECS/npb.spec created; type minimal, rpm version >= 4.16.
```

The resulting file looks like this:
```
Name:           npb
Version:        
Release:        1%{?dist}
Summary:        

License:        
URL:            
Source0:        

BuildRequires:  
Requires:       

%description

%prep
%autosetup

%build
%configure
%make_build

%install
rm -rf $RPM_BUILD_ROOT
%make_install


%files
%license add-license-file-here
%doc add-docs-here

%changelog
* Tue Oct 05 2021 Jose Vicente Nunez <kodegeek.com@protonmail.com>
-  
```

Will remove the following tags from this skeleton file as they are not applicable to our task:
* %autosetup (we will unpack the software ourselves, no patches)
* %configure and %make_build (we will use Gradle)

And will add a few other commands.

Finally let's install the pre-requisites (Java and Gradle itself):

```shell=
sudo dnf install -y java-11-openjdk
sudo -i /bin/mkdir -p /opt/gradle
sudo -i /bin/curl --silent --location --fail --output /opt/gradle/gradle.zip https://services.gradle.org/distributions/gradle-7.2-bin.zip
cd /opt/gradle && sudo /usr/bin/unzip gradle.zip && sudo /bin/rm -f /opt/gradle/gradle.zip
```

Now we are ready to change the SPEC file

### Filling the building blocks for our Java RPM

After [several changes](https://github.com/josevnz/tutorials/blob/main/npb.spec), like adding Gradle as part of the build we have the following:

```
Name:           NPB
Version:        3.0
Release:        1%{?dist}
Summary:        Small set of programs designed to help evaluate the performance of parallel supercomputers

License:        NOSA
URL:            https://www.nas.nasa.gov/software/npb.html
Source0:        https://www.nas.nasa.gov/assets/npb/%{name}%{version}.tar.gz

BuildRequires:  java-11-openjdk-headless,tar,gzip,rpmdevtools,rpmlint
Requires:       java-11-openjdk-headless

# Custom macros (https://rpm-software-management.github.io/rpm/manual/macros.html)
# If you want to see the value of many of these macros, just run this: /usr/bin/rpm --showrc
%global debug_package %{nil}
%global gradle /opt/gradle/gradle-7.2/bin/gradle
%global curl /bin/curl --location --fail --silent --output
%global JAVA_DIR NPB3_0_JAV

%description

The NAS Parallel Benchmarks (NPB) are a small set of programs designed to help evaluate the performance
of parallel supercomputers. The benchmarks are derived from computational fluid dynamics (CFD)
applications and consist of five kernels and three pseudo-applications in the original "pencil-and-paper"
specification (NPB 1). The benchmark suite has been extended to include new benchmarks for unstructured
adaptive meshes, parallel I/O, multi-zone applications, and computational grids. Problem sizes in NPB are
predefined and indicated as different classes. Reference implementations of NPB are available in
commonly-used programming models like MPI and OpenMP (NPB 2 and NPB 3).

%prep
test ! -x %{gradle} && echo "ERROR: Gradle not installed!" && exit 100
# On a production environment you MOST LIKELY point to your private copy of the build artifacts
/bin/curl --location --fail --silent --output %{_sourcedir}/%{name}%{version}.tar.gz  https://www.nas.nasa.gov/assets/npb/%{name}%{version}.tar.gz
%setup -q -n %{name}%{version}

%build
cd %{name}%{version}-JAV
# If you are not familiar with Gradle, you should read the following:
# https://docs.gradle.org/current/userguide/building_java_projects.html#sec:custom_java_source_set_paths
/bin/cat<<GRADLE>build.gradle.kts
// Gradle build file dynamically created for %{name}%{version}
plugins {
    \`java-library\`
}

java {
    toolchain {
        languageVersion.set(JavaLanguageVersion.of(11))
    }   
}

sourceSets {
    main {
        java {
            setSrcDirs(listOf("%{JAVA_DIR}"))
        }
    }   

    test {
        java {
            setSrcDirs(listOf("test"))
        }
    }   
}
GRADLE
%{gradle} clean java jar

%install
/bin/rm -rf %{buildroot}
/bin/mkdir -v -p %{buildroot}/%{_bindir}
/bin/mkdir -v -p %{buildroot}/%{_libdir}
/bin/mkdir -v -p %{buildroot}/%{_pkgdocdir}
/bin/cp -p -v %{_builddir}/%{name}%{version}/%{name}%{version}-JAV/build/libs/%{name}%{version}-JAV.jar %{buildroot}/%{_libdir}

# On a production environment you MOST LIKELY point to your private copy of the build artifacts
%{curl} %{buildroot}/%{_pkgdocdir}/LICENSE https://raw.githubusercontent.com/josevnz/%{name}%{version}-JAV-FORK/main/LICENSE
%{curl} %{buildroot}/%{_pkgdocdir}/README.md https://github.com/josevnz/%{name}%{version}-JAV-FORK/blob/main/%{name}%{version}-JAV/README.md
%{curl} %{buildroot}/%{_bindir}/testAllS https://raw.githubusercontent.com/josevnz/tutorials/main/testAllS
%{curl} %{buildroot}/%{_bindir}/testAllW https://raw.githubusercontent.com/josevnz/tutorials/main/testAllW
/bin/chmod a+xr %{buildroot}/%{_bindir}/{testAllS,testAllW}

%clean
/bin/rm -rf %{buildroot}

%files
%license %{_pkgdocdir}/LICENSE
%doc %{_pkgdocdir}/README.md
%{_libdir}/%{name}%{version}-JAV.jar
%{_bindir}/testAllS
%{_bindir}/testAllW

%changelog
* Tue Oct 05 2021 Jose Vicente Nunez <kodegeek.com@protonmail.com>
- First RPM 

```

The SPEC file is heavily commented and you can see how I used the original tar.gz file without any changes and added a new build system on top of that, plus two ([1](https://github.com/josevnz/tutorials/blob/main/testAllS), [2](https://github.com/josevnz/tutorials/blob/main/testAllW)) wrapper scripts to run the Java code after is installed.

Let's create the new RPM:

```shell=
[josevnz@dmaf5 ~]$ rpmbuild -ba ~/rpmbuild/SPECS/npb.spec
Requires: /usr/bin/bash
Checking for unpackaged file(s): /usr/lib/rpm/check-files /home/josevnz/rpmbuild/BUILDROOT/NPB-3.0-1.fc33.x86_64
Wrote: /home/josevnz/rpmbuild/SRPMS/NPB-3.0-1.fc33.src.rpm
Wrote: /home/josevnz/rpmbuild/RPMS/x86_64/NPB-3.0-1.fc33.x86_64.rpm
Executing(%clean): /bin/sh -e /var/tmp/rpm-tmp.JGJ4Ky
```

Then install it:
```shell=
[josevnz@dmaf5 ~]$ sudo rpm -ihv /home/josevnz/rpmbuild/RPMS/x86_64/NPB-3.0-1.fc33.x86_64.rpm
[sudo] password for josevnz: 
Verifying...                          ################################# [100%]
Preparing...                          ################################# [100%]
Updating / installing...
   1:NPB-3.0-1.fc33                   ################################# [100%]


```

### How does it look like?

```shell=
/usr/bin/testAllS
+ /usr/lib/jvm/java-11-openjdk-11.0.12.0.7-4.fc33.x86_64/bin/java -classpath /home/josevnz/rpmbuild/BUILD/NPB3.0/NPB3.0-JAV/build/libs/NPB3.0-JAV.jar NPB3_0_JAV.BT -np2 CLASS=S
 NAS Parallel Benchmarks Java version (NPB3_0_JAV)
 Multithreaded Version BT.S np=2
No input file inputbt.data, Using compiled defaults
Size: 12 X 12 X 12
Iterations: 60 dt: 0.01
Time step 1
Time step 20
Time step 40
Time step 60
Verification being performed for class S
accuracy setting for epsilon = 1.0000000000000005E-8
Comparison of RMS-norms of residual
0. 0.1703428370954122 0.17034283709541312 5.377003288977261E-15
1. 0.012975252070034126 0.012975252070034096 2.2728112665889987E-15
2. 0.032527926989483404 0.032527926989486054 8.148866886442929E-14
3. 0.026436421275142053 0.0264364212751668 9.361163090380881E-13
4. 0.1921178413174506 0.1921178413174443 3.279505756228626E-14
Comparison of RMS-norms of solution error
0. 4.997691334580433E-4 4.997691334581158E-4 1.4513326350787734E-13
1. 4.519566678297316E-5 4.519566678296193E-5 2.484368424681786E-13
2. 7.397376517295259E-5 7.397376517292135E-5 4.222926198459033E-13
3. 7.382123863238472E-5 7.382123863243973E-5 7.451745425239995E-13
4. 8.926963098749218E-4 8.926963098749145E-4 8.258771422427503E-15
BT.S: Verification Successful

```


## What did we learn and what is next?

Packaging software with RPM looks intimidating at first, but with a little bit of pacience you will get there in no time. As you encounter issue you will also find proper ways to improve your code. Below are some resources and final recommendations:

* Do yourself a big favor and get a copy of the [RPM Packaging Guide](https://rpm-packaging-guide.github.io/) written by dam Miller, Maxim Svistunov, Marie Doleželová. It is very complete, very well organized. Seriously, do it now, it is that good!
* The [Fefora RPM guide](https://docs.fedoraproject.org/en-US/Fedora_Draft_Documentation/0.1/html/RPM_Guide/ch-command-reference.html#id741230) is also full of details, keep it a bookmark away.
* Use [rpmlint](https://github.com/rpm-software-management/rpmlint). You will be surprised how many little things you can catch and fix before shipping your RPM packages
* Not enough? Fedora has [a list of tricks](https://fedoraproject.org/wiki/Packaging_tricks) you can use when packaging software.
* Still thirsty? Good, the Rabbit hole goes deep Neo. You should definitely take a lootk at [RPM Packaging guidelines](https://docs.fedoraproject.org/en-US/packaging-guidelines/SourceURL/)



