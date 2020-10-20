FROM ubuntu

RUN apt-get update -y -qq
RUN apt-get install -y -qq locales
RUN sed -i -e 's/# en_US.UTF-8 UTF-8/en_US.UTF-8 UTF-8/' /etc/locale.gen && \
    locale-gen

ENV LANG en_US.UTF-8  
ENV LANGUAGE en_US:en  
ENV LC_ALL en_US.UTF-8   

RUN apt-get install -y -qq python3 build-essential libpython3-dev python3-dev git wget
RUN ln -s /usr/bin/python3 /usr/bin/python

RUN mkdir -p ~/.ssh/
COPY ssh /root/.ssh    
RUN ssh-keyscan -t rsa github.com >> ~/.ssh/known_hosts && \
    git config --global url."git@github.com:".insteadOf "https://github.com/"

RUN mkdir -p ~/scripts/
COPY scripts /root/scripts
RUN chmod +x /root/scripts/kodo_clone_and_build.sh

RUN mkdir -p ~/libs