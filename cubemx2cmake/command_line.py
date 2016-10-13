from pkg_resources import resource_filename
import sys
from configparser import ConfigParser
from string import Template


def main():
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
    except Exception:
        print("No input file was specified!")
        exit(0)
    
    cube_config = ConfigParser()
    try:
        cube_config.read_string(u"[section]\n"+open(cube_file).read())
    except Exception:
        print("Input file doesn't exist, is broken or access denied.")
        exit(0)
    cube_config = dict(cube_config["section"])
    
    try:
        mcu_name = cube_config["mcu.name"]
        mcu_username = cube_config["mcu.username"]
        mcu_family = cube_config["mcu.family"]+"xx"
        prj_name = cube_config["projectmanager.projectname"]
    except Exception:
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
    
    try:
        with open(resource_filename(__name__, "CMakeLists.txt.template"), "r") as cmakelists_template:
            with open("CMakeLists.txt", "w") as cmakelists:
                cmakelists.write(Template(cmakelists_template.read()).safe_substitute(cmakelists_params))
        with open(resource_filename(__name__, "STM32Toolchain.cmake.template"), "r") as toolchain_template:
            with open("STM32Toolchain.cmake", "w") as toolchain:
                toolchain.write(Template(toolchain_template.read()).safe_substitute(toolchain_params))
    except Exception:
        print("Cannot write output files! Maybe write access to the current directory is denied.")
        exit(0)

    print("CMakeLists.txt and STM32Toolchain.cmake were successfully generated!")
