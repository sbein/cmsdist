### RPM external condorpy3 9.2.0
## INITENV +PATH LD_LIBRARY_PATH %i/lib/condor
## INITENV +PATH PYTHONPATH %i/${PYTHON_LIB_SITE_PACKAGES}
%define condortag %(echo V%realversion | tr "." "_")

Source: git://github.com/htcondor/htcondor.git?obj=master/%{condortag}&export=condor-%{realversion}&output=/condor-%{realversion}.tar.gz
Patch0: cms-htcondor-build
Patch1: condor-vomsapi-static

Requires: zlib expat pcre libtool boost175py3 p5-archive-tar curl libxml2 p5-time-hires libuuid sqlite
BuildRequires: cmake gcc python3 py3-setuptools

%prep
%setup -n condor-%{realversion}
%patch0 -p1
%patch1 -p1

%build
export CMAKE_INCLUDE_PATH=${LIBTOOL_ROOT}/include:${ZLIB_ROOT}/include:${PCRE_ROOT}/include:${BOOST175PY3_ROOT}/include:${EXPAT_ROOT}/include:${CURL_ROOT}/include:${LIBXML2_ROOT}/include:${LIBUUID_ROOT}/include:${SQLITE_ROOT}/include
export CMAKE_LIBRARY_PATH=${LIBTOOL_ROOT}/lib:${ZLIB_ROOT}/lib:${PCRE_ROOT}/lib:${BOOST175PY3_ROOT}/lib:${EXPAT_ROOT}/lib:${CURL_ROOT}/lib:${LIBXML2_ROOT}/lib:${LIBUUID_ROOT}/lib:${SQLITE_ROOT}/lib
export CXXFLAGS="-I${LIBTOOL_ROOT}/include -I$ZLIB_ROOT/include -I$PCRE_ROOT/include -I$BOOST175PY3_ROOT/include -I$EXPAT_ROOT/include -I$CURL_ROOT/include -I$LIBXML2_ROOT/include -I${LIBUUID_ROOT}/include -I${SQLITE_ROOT}/include"
export LDFLAGS="-L${LIBTOOL_ROOT}/lib -L$ZLIB_ROOT/lib -L$PCRE_ROOT/lib -L$BOOST175PY3_ROOT/lib -L$EXPAT_ROOT/lib -L$CURL_ROOT/lib -L$LIBXML2_ROOT/lib -L${LIBUUID_ROOT}/lib -L${SQLITE_ROOT}/lib"
export CFLAGS="$CXXFLAGS"

cmake \
  -DCMAKE_INSTALL_PREFIX=%i \
  -DPROPER:BOOL=OFF \
  -DBUILD_TESTING:BOOL=OFF \
  -DBoost_INCLUDE_DIR:PATH=$BOOST175PY3_ROOT/include \
  -DBoost_LIBRARY_DIRS:FILEPATH=$BOOST175PY3_ROOT/lib \
  -DBoost_THREAD_LIBRARY:FILEPATH=$BOOST175PY3_ROOT/lib/libboost_thread.so \
  -DBoost_THREAD_LIBRARY_DEBUG:FILEPATH=$BOOST175PY3_ROOT/lib/libboost_thread.so \
  -DBoost_THREAD_LIBRARY_RELEASE:FILEPATH=$BOOST175PY3_ROOT/lib/libboost_thread.so \
  -DBoost_PYTHON_LIBRARY:FILEPATH=$BOOST175PY3_ROOT/$PYTHON_LIB_SITE_PACKAGES \
  -DUW_BUILD:BOOL=ON \
  -DWITH_GLOBUS:BOOL=ON \
  -DWITH_CREAM:BOOL=OFF \
  -DWITH_PYTHON_BINDINGS:BOOL=ON \
  -DWITH_VOMS:BOOL=ON \
  -DHAVE_SSH_TO_JOB:BOOL=OFF \
  -DWITH_COREDUMPER:BOOL=OFF \
  -DWITH_DRMAA:BOOL=OFF \
  -DWITH_GSOAP:BOOL=OFF \
  -DWITH_BLAHP:BOOL=OFF \
  -DWITH_KRB5:BOOL=OFF \
  -DWITH_LIBCGROUP:BOOL=OFF \
  -DWITH_LIBVIRT:BOOL=OFF \
  -DLDAP_FOUND_SEARCH_lber:PATH=LDAP_FOUND_SEARCH_lber-NOTFOUND \
  -DLDAP_FOUND_SEARCH_ldap:PATH=LDAP_FOUND_SEARCH_ldap-NOTFOUND \
  -DWITH_UNICOREGAHP:BOOL=OFF \
  -DWITH_LIBDELTACLOUD:BOOL=OFF \
  -DPYTHON_EXECUTABLE:FILEPATH=${PYTHON3_ROOT}/bin/python3.8 \
  -DPYTHON_INCLUDE_DIR:PATH=${PYTHON3_ROOT}/include/python3.8 \
  -DPYTHON_LIBRARY:FILEPATH=${PYTHON3_ROOT}/lib/libpython3.8.so \
  -DEXPAT_FOUND_SEARCH_expat:FILEPATH=${EXPAT_ROOT}/lib/libexpat.so \
  -DCLIPPED:BOOL=ON \
  -DWITH_BOINC:BOOL=OFF \
  -DWITH_SCITOKENS:BOOL=OFF \
  -DCMAKE_SKIP_RPATH:BOOL=ON

# Use makeprocess macro, it uses compiling_processes defined by
# build configuration file or build argument
make %makeprocesses VERBOSE=1 externals
make %makeprocesses VERBOSE=1

%install
make install

# Move the python-bindings to the correct place
mkdir -p %i/$PYTHON_LIB_SITE_PACKAGES
mv %i/lib/python/* %i/$PYTHON_LIB_SITE_PACKAGES
# Get rid of hardcoded /usr/bin/python
egrep -r -l '^#!.*python' %i | xargs perl -p -i -e 's{^#!.*python.*}{#!/usr/bin/env python}'

# Strip libraries, we are not going to debug them.
%define strip_files %i/lib

# Clean things up; read the docs online;
# remove condor_gather_info since it brings a dependency on Date::Manip
rm -rf %i/{README,etc/{examples,init.d,sysconfig},examples} \
       %i/{include,sbin,libexec,src,condor*,bosco*}         \
       %i/bin/{condor_gather_info,bosco*} %i/lib/python     \
       %i/lib/condor/{libcom*,libcrypto*,libk*,libl*,libp*} \
       %i/lib/condor/{libssl*,libgssapi_krb5*,libexpat*1}

# Generate dependencies-setup.{sh,csh} so init.{sh,csh} picks full environment.
mkdir -p %i/etc/profile.d
: > %i/etc/profile.d/dependencies-setup.sh
: > %i/etc/profile.d/dependencies-setup.csh
for tool in $(echo %{requiredtools} | sed -e's|\s+| |;s|^\s+||'); do
  root=$(echo $tool | tr a-z- A-Z_)_ROOT; eval r=\$$root
  if [ X"$r" != X ] && [ -r "$r/etc/profile.d/init.sh" ]; then
    echo "test X\$$root != X || . $r/etc/profile.d/init.sh" >> %i/etc/profile.d/dependencies-setup.sh
    echo "test X\$?$root = X1 || source $r/etc/profile.d/init.csh" >> %i/etc/profile.d/dependencies-setup.csh
  fi
done

%post
%{relocateConfig}etc/profile.d/dependencies-setup.*sh
