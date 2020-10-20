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

Before we build the docker image we need to setup a few things. 
In the folder containing the Docker file (`distributed-storage-labs/Docker`), create a folder name `ssh`.
First copy the ssh key you generate earlier, if you didn't give it a custom name and path, the name will be `id_rsa`. 
You need to copy both `id_rsa` and `id_rsa.pub`. 
Next in the `ssh` folder create a file name `config`, the content of this file should be: 

```bash
host github.com
    Hostname        github.com
    User            git
    IdentityFile    ~/.ssh/id_rsa
```

If you have chosen a different name for your SSH key file change `id_rsa` for the option `IdentityFile` accordingly. 

Next we build the docker image: 

```bash
docker build -t distributed-storage .
```

This will download latest official Ubuntu image and setup python and everything else you need for this course.


# Building Kodo 

Before you continue with the exercises we need to build Kodo. 
First make a directory which you will use as persistent data storage for the Docker container (they are not persistent by default).
We will assume that you have called the folder `libs` and that is located in the same folder as the Docker file. 
Next we start our container: 

```bash 
    docker run -it --rm -v FULL_SYSTEM_PATH/distributed-storage-labs/Docker/libs/:/root/libs --entrypoint bash dist-kodo:latest
```

The full system path is from ROOT and all the way down to the final sub-folder `/root/libs` is the "mount point" in the container.
This is the command you will use to run the container in the future. 
`--entrypoint bash` gives us a bash terminal instead of the container immediately terminating.

Next, step to ensure that we do not have to type our ssh passphrase over and over. 
We invoke the ssh-agen and add the `id_rsa` key (again if you changed the name, adopt) and enter the passphrase. 

```Bash
    ssh-agent bash
    ssh-add /root/.ssh/id_rsa
```

Next run:

```bash
./root/scripts/kodo_clone_and_build.sh
```

This script clone, configures, and build kodo-python for you and copy `kodo.so` (full name will vary) file in `/root/libs` (which our external folder).
It also runs the `encode_decode_simple.py` example from kodo-python, if you notice any errors something is afoot. 

Congratulations, you now have a working Docker image than can be used for working with kodo-python. 

# Installing other needed tools. 

TBW 

# Exercises in general

TBW 

