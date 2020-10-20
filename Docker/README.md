# Docker setup for Distributed Storage 

## Installing Docker 

Depending on your operating system docker is installed differently but the [get Docker guide](https://docs.docker.com/get-docker/) covers most operating systems. 

## Create a GitHub and GitLab account

To solve the exercises for this course you will need a GitHub and GitLab account, the GitLab account is need for getting a Kodo Research license (see Get Kodo license section) 
Both can be obtained for free and we recommend that you sign up for a GitHub education, account.
You can apply for the GitHub education account after you sign up for the free account

Github: [signup](https://github.com/join?ref_cta=Sign+up&ref_loc=header+logged+out&ref_page=%2F&source=header-home)

GiLab: [signup](https://gitlab.com/users/sign_in#register-pane)


## Get a Kodo license

In this course we will cover Reed-Solomon (RS) and Random Linear Network (RLNC) Codes.
For this we will use the software library [Kodo](https://www.steinwurf.com/products/kodo.html) and for this you will need a research license, which you need to apply for [here](https://www.steinwurf.com/license.html).

It can take some time for the license to be approve, so apply as early as possible. 

## Installing Git

You can find the official git install instructions here: https://git-scm.com/downloads

### Mac 

We recommend that you use [Homebrew](https://brew.sh/) to install and manage git. 
Simply type `brew install git`.

### Linux

If your distribution of choice does not come with git preinstalled it is available in your default package repository, with the package name `git` or `git-scm`.
Below are installation instructions for some Linux distributions. 

__Fedora:__ `dnf install -y git`

__Debian/Ubuntu/Mint/:__ `apt-get install -y git`


### Windows 

Install [Git Bash](https://git-scm.com/download/win)

## Installing Docker 

## Setting up SSH 

When you use Git it is beneficial to use SSH keys for authentication, as you have to type your password a lot less.
GitHub provides a guide for this: [https://docs.github.com/en/free-pro-team@latest/github/authenticating-to-github/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent](https://docs.github.com/en/free-pro-team@latest/github/authenticating-to-github/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent)



## Building the Docker image 

You will need the ssh-key we generated earlier.
Place it in `ssh` folder of this folder. 

To build the image run:

```bash 
    docker build build -t distributed-storage .
    
    docker run -it --rm -v FULL_SYSTEM_PATH/distributed-storage-labs/Docker/libs/:/root/libs --entrypoint bash dist-kodo:latest
```

# Building Kodo 

```Bash
    ssh-agent bash
    ssh-add /root/.ssh/id_rsa
```

