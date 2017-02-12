""" This is the implementation of cubemx2cmake command """

import sys
import os
import six
import logging
from argparse import ArgumentParser
from six.moves import configparser
from string import Template
from pkg_resources import resource_filename


class LoggingCriticalHandler(logging.Handler):
    def emit(self, record):
        logging.shutdown()
        exit(1)


def main():
    """ Function entry point for running script from command line """
    _main(sys.argv[1:])


def _main(args):
    """ Runnable code with CLI args for testing convenience"""
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

    logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.INFO)
    logging.getLogger().addHandler(LoggingCriticalHandler(logging.CRITICAL))

    arg_parser = ArgumentParser()
    arg_parser.add_argument("cube_file", default="", nargs='?',
                            help="CubeMX project file (if not specified, the one contained in current directory is "
                                 "used)")
    arg_parser.add_argument("-i", "--interface", default="stlink-v2",
                            help="OpenOCD debug interface name (stlink-v2 is used by default)")
    arg_parser.add_argument("-m", "--memory-start", default="0x08000000",
                            help="Flash memory start address (0x08000000 by default)")
    arg_parser.add_argument("-g", "--gdb-port", default="3333",
                            help="The port for connecting with GDB")
    arg_parser.add_argument("-t", "--telnet-port", default="4444",
                            help="The port for connecting via telnet")
    args = arg_parser.parse_args(args)

    if args.cube_file != "":
        cube_file = args.cube_file
    else:
        ioc_files = []
        # Check if there is a single *.ioc file
        logging.info("No input file was specified. Searching for a *.ioc file in the current directory.")
        for file in os.listdir("."):
            if file.endswith(".ioc"):
                ioc_files.append(file)
        if len(ioc_files) == 1:
            cube_file = ioc_files[0]
            logging.info("%s file was found", cube_file)
        else:
            logging.critical("%d *.ioc files were found. You need to specify an input file manually",
                             len(ioc_files))

    cube_config_parser = configparser.ConfigParser()
    try:
        # *.ioc files have a INI-like format, but without section, so we need to create one
        cube_config_parser.read_string(u"[section]\n" + open(cube_file).read())
    except FileNotFoundError:
        logging.critical("Input file doesn't exist!")
    except IOError:
        logging.critical("Input file doesn't exist, is broken or access denied.")

    # Get the data from the fake section we created earlier
    # Lower all keys for compatibility with older versions of CubeMX
    cube_config = dict((k.lower(), v) for k, v in six.iteritems(dict(cube_config_parser["section"])))

    try:
        mcu_family = cube_config["mcu.family"]
        mcu_username = cube_config["mcu.username"]
        prj_name = cube_config["projectmanager.projectname"]
        toolchain = cube_config["projectmanager.targettoolchain"]
        generate_under_root = cube_config["projectmanager.underroot"]
    except KeyError:
        logging.critical("Failed to parse the input file. Maybe it is corrupted.\nIf you think it isn't report to "
                         "https://github.com/eugene-babichenko/cubemx2cmake issues section")

    if toolchain != "SW4STM32":
        logging.critical("Wrong toolchain! SW4STM32 should be used with this script")
    if generate_under_root != "true":
        logging.critical("'Generate under root' should be applied!")

    params = {
        "PRJ_NAME": prj_name,
        "MCU_FAMILY": mcu_family + "xx",
        "MCU_LINE": mcu_username[:9] + "x" + cube_config["mcu.name"][13],
        "MCU_LINKER_SCRIPT": mcu_username + "_FLASH.ld",
        "MCU_ARCH": architecture[mcu_family + "xx"],
        "TARGET": mcu_family + "x",
        "INTERFACE_NAME": args.interface,
        "GDB_PORT": args.gdb_port,
        "TELNET_PORT": args.telnet_port
    }

    logging.info("Successfully read %s", cube_file)
    logging.info("Generating output files...")

    templates = os.listdir(resource_filename(__name__, "templates"))

    for template_name in templates:
        template_fn = resource_filename(__name__, "templates/%s" % template_name)
        with open(template_fn, "r") as template_file:
            template = Template(template_file.read())
        try:
            output_name = template_name.split(".template")[0]
            with open(output_name, "w") as target_file:
                logging.info("Writing %s...", output_name)
                target_file.write(template.safe_substitute(params))
        except IOError:
            logging.critical("Cannot write output files! Maybe write access to the current directory is denied.")

    logging.info("All files were successfully generated!")
    logging.shutdown()
