### RPM external py2-pycurl 7.43.0
## INITENV +PATH PYTHONPATH %{i}/$PYTHON_LIB_SITE_PACKAGES


%define pip_name pycurl
Requires: curl

## IMPORT build-with-pip

