#!/bin/bash
git clone --depth 1 --branch 4.6.0 https://github.com/opencv/opencv.git
cd opencv
mkdir build
cd build
cmake .. -DBUILD_LIST=core,imgproc
cmake --build .
cmake --install .