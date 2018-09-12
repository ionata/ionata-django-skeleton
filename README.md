# Ionata Django Skeleton

## Base Django project

A django-configurations based project

Intended for use with https://github.com/ionata/ionata-django-settings

Docker image for the backend is from https://gitlab.com/ionata/django-images

If you don't have access, it's basically:

* ubuntu 16.04
* install build tools:  
  `build-essential`, `g++-5`, `gettext`, `git`, `libjpeg-dev`, `locales`, `zlib1g-dev`
* install postgis requirements  
  `binutils`, `gdal-bin`, `libpq-dev`, `libproj-dev`, `libgeos-dev`, `postgis`, `postgresql-client`
* install mssql requirements  
  `msodbcsql`, `mssql-tools`, `unixodbc-dev`
* install wkhtmltopdf+libfontconfig
* install python3.7+pipenv
* install nginx
