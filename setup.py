from setuptools import setup

def readme():
    with open('README.rst') as f:
        return f.read()

setup(
	name='cubemx2cmake',
	version='1.0.1',
	description='Command line tool to generate CMakeLists.txt from STM32CubeMX projects.',
	long_description=readme(),
	classifiers=[
		'Topic :: Software Development :: Code Generators',
		'Topic :: Utilities'
	],
	keywords='st stm32 cube cubemx stm32cubemx cmake code generator',
	url='https://github.com/eugene-babichenko/cubemx2cmake',
	author='Yevhenii Babichenko',
	email='eugene.babichenko@gmail.com',
	license='MIT',
	packages=['cubemx2cmake'],
	zip_safe=False,
	include_package_data=True,
	entry_points={'console_scripts': ['cubemx2cmake=cubemx2cmake.command_line:main']}
)
