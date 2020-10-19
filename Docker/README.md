# Docker setup for Distributed Storage 

## Installing Docker 

Depending on your operating system docker is installed differently but the [get Docker guide](https://docs.docker.com/get-docker/) covers most operating systems. 

## Create a Github Client

TBW

## Get a Kodo license

In this course we will cover Reed-Solomon (RS) and Random Linear Network (RLNC) Codes.
For this we will use the software library [Kodo](https://www.steinwurf.com/products/kodo.html) and for this you will need a research license, which you need to apply for [here](https://www.steinwurf.com/license.html).

It can take some time for the license to be approve, so apply as early as possible. 

## Setting up SSH 

### Linux and MacOS 

### Windows 

Good luck

## Building the Docker image 

You will need the ssh-key we generated earlier.
Place it in `ssh` folder of this folder. 

To build the image run:

```bash 
    docker build build -t distributed-storage .
```


