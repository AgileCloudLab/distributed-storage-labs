FROM ubuntu

RUN apt-get update -y -qq
RUN apt-get install -y -qq locales
RUN sed -i -e 's/# en_US.UTF-8 UTF-8/en_US.UTF-8 UTF-8/' /etc/locale.gen && \
    locale-gen

ENV LANG en_US.UTF-8  
ENV LANGUAGE en_US:en  
ENV LC_ALL en_US.UTF-8   

RUN apt-get install -y -qq python3 build-essential libpython3-dev python-dev git wget
RUN rm /usr/bin/python
RUN ln -s /usr/bin/python3 /usr/bin/python

# Downlod course material 
# RUN wget  

# Cloning and building kodo-python 
RUN git clone git@github.com:steinwurf/kodo-python.git
RUN cd kodo-python && ./waf configure && ./waf build && ./waf test

# 


