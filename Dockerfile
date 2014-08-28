FROM ga_base 

ADD . /home/docker/geoanalytics
WORKDIR /home/docker/geoanalytics

EXPOSE 22 80 8000 443 1338

RUN useradd docker -s /bin/bash -d /home/docker
RUN echo 'docker:docker' | chpasswd
RUN chown -R docker:docker /home/docker
VOLUME ["/home/docker/th_cms/terrahub/static/media"]

WORKDIR /home/docker
RUN npm install carto

WORKDIR /home/docker/th_cms
CMD /bin/bash
