FROM ubuntu

RUN apt-get update
RUN apt-get install -y python2.7-mapnik python2.7-scipy python2.7-numpy python2.7-psycopg2 cython python2.7-pysqlite2  nodejs npm python-virtualenv  postgresql-9.3 postgresql-client-common postgresql-common postgresql-client-9.3 redis-tools  sqlite3 sqlite3-pcre libspatialite-dev libspatialite5 spatialite-bin  ssh git libfreetype6 libfreetype6-dev libxml2-dev libxslt-dev libprotobuf-dev  python2.7-gdal gdal-bin libgdal-dev gdal-contrib python-pillow protobuf-compiler libtokyocabinet-dev tokyocabinet-bin libreadline-dev ncurses-dev python2.7-lxml python2.7-pandas  nginx gettext zip unzip

ADD . /root
WORKDIR /root
RUN pip install -r requirements.txt
RUN rm -rf /tmp/pip-build-root
WORKDIR /root/pysqlite-2.6.3/
RUN python setup.py install
WORKDIR /home/docker
RUN rm -rf /root/pysqlite-2.6.3/
RUN pip install cython
RUN pip install numexpr

RUN npm install carto
RUN ln -s /usr/bin/nodejs /usr/bin/node

CMD /bin/bash
