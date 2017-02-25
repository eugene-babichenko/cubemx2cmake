#!/usr/bin/env bash

# For projects that can be successfully built
set -e
for dir in ./test-data/should-success/*/
do
    cd ${dir}
    cubemx2cmake
    mkdir build
    cd build
    cmake .. -D CMAKE_TOOLCHAIN_FILE=../STM32Toolchain.cmake
    ls
    make
    cd ../..
done

# For projects, that should not be generated
set +e
for dir in ./test-data/should-not-generate/*/
do
    cd ${dir}
    cubemx2cmake
    if [ $? -eq 0 ]
    then
        echo "Generator should fail on this project"
        exit 1
    fi
    cd ..
done
