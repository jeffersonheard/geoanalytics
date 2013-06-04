#!/bin/bash

pip install numpy
pip install scipy
pip install cssutils
export CFLAGS=-I/usr/include/gdal
pip install -r requirements.txt
