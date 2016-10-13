""" This is the implementation of cubemx2cmake command """

import sys
import os
from configparser import ConfigParser
from string import Template
from pkg_resources import resource_filename

# Disable warnings about wrong constant name (pylint counts global variables as constants)
# pylint: disable=C0103


def main():
    """ Function entry point to supress TypeError: 'module' object is not callable  """
    pass

architecture = {
    "STM32L0xx": "-mcpu=cortex-m0",
    "STM32F0xx": "-mcpu=cortex-m0",
    "STM32L1xx": "-mcpu=cortex-m3",
    "STM32F1xx": "-mcpu=cortex-m3",
    "STM32F2xx": "-mcpu=cortex-m3",
    "STM32L4xx": "-mcpu=cortex-m4 -mfpu=hard -mfloat-abi=fpv4-sp-d16",
    "STM32F3xx": "-mcpu=cortex-m4 -mfpu=hard -mfloat-abi=fpv4-sp-d16",
    "STM32F4xx": "-mcpu=cortex-m4 -mfpu=hard -mfloat-abi=fpv4-sp-d16",
    "STM32F7xx": "-mcpu=cortex-m7 -mfpu=hard -mfloat-abi=fpv5-sp-d16"
}

try:
    cube_file = sys.argv[1]
except IndexError:
    ioc_files = []
    # Check if there is a single *.ioc file
    for file in os.listdir("."):
        if file.endswith(".ioc"):
            ioc_files.append(file)
    if len(ioc_files) == 1:
        print(ioc_files[0]+" was found!")
        cube_file = ioc_files[0]
    else:
        print("No input file was specified!")
        exit(0)

cube_config_parser = ConfigParser()
try:
    # *.ioc files have a INI-like format, but without section, so we need to create one
    cube_config_parser.read_string(u"[section]\n"+open(cube_file).read())
except FileNotFoundError:
    print("Input file doesn't exist!")
    exit(0)
except IOError:
    print("Input file doesn't exist, is broken or access denied.")
    exit(0)

# Get the data from the fake section we created earlier
cube_config = dict(cube_config_parser["section"])

try:
    mcu_name = cube_config["mcu.name"]
    mcu_username = cube_config["mcu.username"]
    mcu_family = cube_config["mcu.family"]+"xx"
    prj_name = cube_config["projectmanager.projectname"]
except KeyError:
    print("Input file is broken!")
    exit(0)

cmakelists_params = {
    "PRJ_NAME": prj_name,
    "MCU_FAMILY": mcu_family,
    "MCU_LINE": mcu_username[:9]+"x"+mcu_name[13],
    "MCU_LINKER_SCRIPT": mcu_username+"_FLASH.ld"
}

toolchain_params = {
    "MCU_LINKER_SCRIPT": mcu_username+"_FLASH.ld",
    "MCU_ARCH": architecture[mcu_family]
}

# Load templates from resourser
cmakelists_template_fn = resource_filename(__name__, "CMakeLists.txt.template")
toolchain_template_fn = resource_filename(__name__, "STM32Toolchain.cmake.template")
with open(cmakelists_template_fn, "r") as cmakelists_template:
    cmakelists_template = Template(cmakelists_template.read())
with open(toolchain_template_fn, "r") as toolchain_template:
    toolchain_template = Template(toolchain_template.read())

# We use safe_substitute because CMake has the same variables format, as the template library
try:
    with open("CMakeLists.txt", "w") as cmakelists:
        cmakelists.write(cmakelists_template.safe_substitute(cmakelists_params))
    with open("STM32Toolchain.cmake", "w") as toolchain:
        toolchain.write(toolchain_template.safe_substitute(toolchain_params))
except IOError:
    print("Cannot write output files! Maybe write access to the current directory is denied.")
    exit(0)

print("CMakeLists.txt and STM32Toolchain.cmake were successfully generated!")
