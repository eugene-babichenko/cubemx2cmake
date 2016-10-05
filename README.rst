=================
STM32CubeMX2CMake
=================

Installation
------------
From this repository:
*git clone https://github.com/eugene-babichenko/cubemx2cmake.git*
*cd cubemx2cmake*
*pip install cubemx2cmake*

Usage
-----

Generate your initialization code from STM32CubeMX with the following Code Generation Options:
* Toolchain: SW4STM32
* [X] Generate under root
Then open your project directory and run *cubemx2cmake <your_cube_mx_file>.ioc*. This will generate CMakeLists.txt and STM32Toolchain.cmake files. To get all the things done right use *-DCMAKE_TOOLCHAIN_FILE=STM32Toolchain.cmake* command line option with CMake.
