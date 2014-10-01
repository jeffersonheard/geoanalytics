FROM ga_base 

RUN useradd docker -s /bin/bash -d /home/docker
RUN echo 'docker:docker' | chpasswd
RUN chown -R docker:docker /home/docker
RUN echo "docker ALL=(ALL) ALL" >> /etc/sudoers

ADD . /home/docker/geoanalytics
WORKDIR /home/docker/geoanalytics

EXPOSE 22 80 8000 443 1338
VOLUME ["/home/docker/geoanalytics/geoanalytics/static/media"]

WORKDIR /home/docker/geoanalytics
CMD /bin/bash
