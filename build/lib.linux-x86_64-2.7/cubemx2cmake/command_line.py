""" This is the implementation of cubemx2cmake command """

import sys
import os
from argparse import ArgumentParser
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
    "STM32L4xx": "-mcpu=cortex-m4 -mfloat-abi=hard -mfpu=fpv4-sp-d16",
    "STM32F3xx": "-mcpu=cortex-m4 -mfloat-abi=hard -mfpu=fpv4-sp-d16",
    "STM32F4xx": "-mcpu=cortex-m4 -mfloat-abi=hard -mfpu=fpv4-sp-d16",
    "STM32F7xx": "-mcpu=cortex-m7 -mfloat-abi=hard -mfpu=fpv5-sp-d16"
}

arg_parser = ArgumentParser()
arg_parser.add_argument("cube_file", default="", nargs='?',
    help="CubeMX project file (if not specified, the one contained in current directory is used)")
arg_parser.add_argument("-i", "--interface", default="stlink-v2",
    help="OpenOCD debug interface name (stlink-v2 is used by default)")
arg_parser.add_argument("-m", "--memory-start", default="0x08000000",
    help="Flash memory start address (0x08000000 by default)")
arg_parser.add_argument("-g", "--gdb-port", default="3333",
    help="The port for connecting with GDB")
arg_parser.add_argument("-t", "--telnet-port", default="4444",
    help="The port for connecting via telnet")
args = arg_parser.parse_args()

if args.cube_file != "":
    cube_file = args.cube_file
else:
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
    mcu_family = cube_config["mcu.family"]
    mcu_username = cube_config["mcu.username"]
    prj_name = cube_config["projectmanager.projectname"]
except KeyError:
    print("Input file is broken!")
    exit(0)

params = {
    "CMakeLists.txt": {
        "PRJ_NAME": prj_name,
        "MCU_FAMILY": mcu_family+"xx",
        "MCU_LINE": mcu_username[:9]+"x"+cube_config["mcu.name"][13],
        "MCU_LINKER_SCRIPT": mcu_username+"_FLASH.ld"
    },
    "STM32Toolchain.cmake": {
        "MCU_LINKER_SCRIPT": mcu_username+"_FLASH.ld",
        "MCU_ARCH": architecture[mcu_family+"xx"]
    },
    "openocd_debug.cfg": {
        "TARGET": mcu_family+"x",
        "PRJ_NAME": prj_name,
        "INTERFACE_NAME": args.interface,
        "GDB_PORT": args.gdb_port,
        "TELNET_PORT": args.telnet_port
    },
    "openocd_flash.cfg": {
        "TARGET": mcu_family+"x",
        "PRJ_NAME": prj_name,
        "INTERFACE_NAME": args.interface,
        "FLASH_START": args.memory_start
    }
}

for template_name in params.keys():
    template_fn = resource_filename(__name__, template_name+".template")
    with open(template_fn, "r") as template_file:
        template = Template(template_file.read())
    try:
        with open(template_name, "w") as target_file:
            target_file.write(template.safe_substitute(params[template_name]))
    except IOError:
        print("Cannot write output files! Maybe write access to the current directory is denied.")
        exit(0)

print("All files were successfully generated!")
# TODO: Remove SW4STM32 files
