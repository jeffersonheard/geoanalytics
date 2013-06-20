# Installation instructions for Geoanalytics (GA)
These instructions assume you will install Geoanalytics in your home directory
on a machine running Ubuntu Linux.  Geoanalytics can be installed on RedHat,
but the install process is more manual.`

## Clone GA from GitHub
    git clone https://github.com/JeffHeard/ga_cms.git
### Switch to the develop branch
    git branch develop

## Install required packages for Mapnik and Geoanalytics.
You will need root for this.

    cd ga_cms
    sh requirements/kickstart.ubuntu

## Install Mapnik 2.1.0
    wget https://github.com/mapnik/mapnik/archive/v2.1.0.tar.gz
    tar xvzf mapnik-2.1.0.tar.gz 
    cd mapnik-2.1.0/
    ./configure 
    make
    sudo make install

## Setup virtual env
    cd ~ 
    virtualenv --system-site-packages --distribute geoanalytics
    cd geoanalytics/
    source bin/activate [use this step in the future to jump into the virtual env.]

### Install GA python modules within the virtual env
  cd ga_cms
  sh install.sh

## Create PostGIS database 
see https://docs.djangoproject.com/en/dev/ref/contrib/gis/install/postgis/

### Create database user
    sudo su - postgres
    createuser geoanalytics

Say yes to the folowing questions
> Shall the new role be a superuser? (y/n) n
> Shall the new role be allowed to create databases? (y/n) y
> Shall the new role be allowed to create more new roles? (y/n) n

### Set postgres passwords
    psql
    alter user postgres encrypted password 'YOURSECRETPASSWORD';
    alter user geoanalytics encrypted password 'YOUROTHERSECRETPASSWORD';
    \q

### Create the DB (first log out of postgres shell we su'ed into)
    createdb geoanalytics

## Set up PostGIS spatial extensions on the database
### PostGIS 2 and PostgreSQL 9.1+
    psql geoanalytics
    CREATE EXTENSION postgis;
    CREATE EXTENSION postgis_topology;

### Older version of PostGIS
The above won't work and you will see an error such as:

> ERROR:  could not open extension control file "/usr/share/postgresql/9.1/extension/postgis.control": No such file or directory

In this case, create a template postgis database:

    sudo su - postgres
    sh requirements/create_template_postgis-debian.sh (or use another script from: https://docs.djangoproject.com/en/dev/ref/contrib/gis/install/postgis/)

### Create your database from the PostGIS template
createdb -T template_postgis geoanalytics

## Edit DATABASES section of settings.py as follows
> "ENGINE": "django.contrib.gis.db.backends.postgresql_psycopg2"
> "NAME": "geoanalytics"
> "USER": "geoanalytics"
> "PASSWORD": "YOUROTHERSECRETPASSWORD"

## Initialize the database from the geoanalytics/geodjango side
    python manage.py syncdb

Say yes when prompted to create a Django superuser

python manage.py migrate

## Run the server
    python manage.py runserver


