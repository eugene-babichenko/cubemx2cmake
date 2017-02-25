#!/usr/bin/env bash

# For projects that can be successfully built
set -e
cd ./test-data/should-success/
find . -maxdepth 1 -mindepth 1 -type d -print0 | while IFS= read -r -d $'\0' dir
do
    cd "$dir"
    cubemx2cmake
    rm -rf build
    mkdir build
    cd build
    cmake -D CMAKE_TOOLCHAIN_FILE=../STM32Toolchain.cmake ..
    ls
    make
    cd ../..
done
cd ../..

# For projects, that should not be generated
set +e
cd ./test-data/should-not-generate
find . -maxdepth 1 -mindepth 1 -type d -print0 | while IFS= read -r -d $'\0' file
do
    cd "$dir"
    cubemx2cmake
    if [ $? -eq 0 ]
    then
        echo "Generator should fail on this project"
        exit 1
    fi
    cd ..
done
