=================
STM32CubeMX2CMake
=================

Installation
------------
From this repository:

*git clone https://github.com/eugene-babichenko/cubemx2cmake.git*

*cd cubemx2cmake*

*pip install .*

Or you can install it from PyPI:

*pip install cubemx2cmake*

Usage
-----

Generate your initialization code from STM32CubeMX with the following Code Generation Options:

* Toolchain: SW4STM32
* [X] Generate under root

Then open your project directory and run *cubemx2cmake <your_cube_mx_file>.ioc*. If your working dirctory contains inly one CubeMX project file (*.ioc), you can simply run *cubemx2cmake* and it will find your project file automatically. This will generate CMakeLists.txt and STM32Toolchain.cmake files. To get all the things done right use *-DCMAKE_TOOLCHAIN_FILE=STM32Toolchain.cmake* command line option with CMake.
