Name:           NPB
Version:        3.0
Release:        1%{?dist}
Summary:        Small set of programs designed to help evaluate the performance of parallel supercomputers

License:        NOSA
URL:            https://www.nas.nasa.gov/software/npb.html
Source0:        https://www.nas.nasa.gov/assets/npb/%{name}%{version}.tar.gz

BuildRequires:  java-11-openjdk,tar,gzip,rpmdevtools,rpmlint
Requires:       java-11-openjdk

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

%clean
/bin/rm -rf %{buildroot}

%files
%license %{_pkgdocdir}/LICENSE
%doc %{_pkgdocdir}/README.md
%{_libdir}/%{name}%{version}-JAV.jar

%changelog
* Tue Oct 05 2021 Jose Vicente Nunez <kodegeek.com@protonmail.com>
- First RPM
