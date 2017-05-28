Summary:	Java Simple Serial Connector
Name:		jssc
Version:	2.8.0
Release:	6%{?dist}
License:	GPLv3+
Group:		System Environment/Libraries
URL:		http://jssc.scream3r.org
Source:		https://github.com/scream3r/java-simple-serial-connector/archive/v%{version}.tar.gz#/%{name}-%{version}.tar.gz
# lack of license file, reported upstream:
# https://github.com/scream3r/java-simple-serial-connector/issues/79
Source1:	http://www.gnu.org/licenses/gpl-3.0.txt
# jni load library patch
Patch0:		%{name}-loadlibrary.patch
# fixes jni header mismatch, reported upstream:
# https://github.com/scream3r/java-simple-serial-connector/issues/80
Patch1:		%{name}-jni-fix.patch

BuildRequires:	java-devel
BuildRequires:	javapackages-local

Requires:	java-headless
Requires:	jpackage-utils

%global jni		%{_libdir}/%{name}
%global jniFullSoName	libjSSC-%{version}.so
%global jniSoName	libjSSC.so


%description
jSSC (Java Simple Serial Connector) - library for working with serial ports
from Java.


%package javadoc
Summary:        Javadoc for %{name} package
BuildArch:      noarch
Requires:       %{name} = %{version}


%description javadoc
This package contains the API documentation for %{name}.


%prep
%setup -q -n java-simple-serial-connector-%{version}
%patch0 -p1 -b .loadlibrary
%patch1 -p1 -b .jni-fix
cp -a %{SOURCE1} COPYING
# remove prebuild binaries and jni headers
rm -rf src/java/libs
rm -rf src/cpp/*.h


%build
# compile classes
mkdir -p classes/
(cd src/java; javac -d ../../classes/ -encoding UTF-8 jssc/*.java)
(cd classes; jar -cf ../jssc.jar jssc/*.class)
# generate javadoc
mkdir -p javadoc/
(cd src/java; javadoc -Xdoclint:none -d ../../javadoc/ -encoding UTF-8 jssc/*.java)
# generate jni header
(cd classes; javah -jni -d ../src/cpp -encoding UTF-8 jssc.SerialNativeInterface)
# compile native library
%setup_compile_flags
$(CXX) %{optflags} %{?__global_ldflags} -std=c++11 -fPIC -shared \
    -D jSSC_NATIVE_LIB_VERSION=\"$(echo %{version} | sed 's/\([1-9]\.[0-9]\).*/\1/')\" \
    -I %{java_home}/include \
    -I %{java_home}/include/linux \
    -o %{jniFullSoName} src/cpp/_nix_based/jssc.cpp


%install
# create necessary directories
install -d %{buildroot}%{jni} \
           %{buildroot}%{_javadocdir}/%{name}
# install jni library and symlink
install -m 0755 -p %{jniFullSoName} %{buildroot}%{jni}
ln -srf %{buildroot}%{jni}/%{jniFullSoName} %{buildroot}%{jni}/%{jniSoName}
# install jar, pom files and java docs
%mvn_artifact org.scream3r:%{name}:%{version} %{name}.jar
%mvn_file org.scream3r:%{name}:%{version} %{name}
%mvn_install -J javadoc


%files -f .mfiles
%doc COPYING
%doc README.txt
%{jni}/


%files javadoc
%doc %{_javadocdir}/%{name}


%changelog
* Fri Feb 10 2017 Fedora Release Engineering <releng@fedoraproject.org> - 2.8.0-6
- Rebuilt for https://fedoraproject.org/wiki/Fedora_26_Mass_Rebuild

* Thu Feb 04 2016 Fedora Release Engineering <releng@fedoraproject.org> - 2.8.0-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Sat Dec 05 2015 Damian Wrobel <dwrobel@ertelnet.rybnik.pl> - 2.8.0-4
- Simplify BR, install and files sections.

* Wed Nov 25 2015 Damian Wrobel <dwrobel@ertelnet.rybnik.pl> - 2.8.0-3
- Change the license to GPLv3.

* Thu Nov 12 2015 Damian Wrobel <dwrobel@ertelnet.rybnik.pl> - 2.8.0-2
- Use URL fragment to automatically rename source tarball.

* Mon Nov 02 2015 Damian Wrobel <dwrobel@ertelnet.rybnik.pl> - 2.8.0-1
- Initial RPM release.
