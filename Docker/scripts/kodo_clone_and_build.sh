#!/usr/bin/env bash
cd root/scripts/
git clone git@github.com:steinwurf/kodo-python.git
cd kodo-python
./waf configure build
cp ./build/linux/kodo*.so examples
cd examples
python encode_decode_simple.py
cp kodo*.so /root/libs
