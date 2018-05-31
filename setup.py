from distutils.core import setup, Extension

module1 = Extension('spi', sources = ['spi.c'])

setup (
    name = 'SPI-Py',
    author='Erwin Suarez',
    url='https://github.com/ErwinSuarez/MFRC522forPi',
    download_url='https://github.com/ErwinSuarez/MFRC522forPi/archive/master.zip',
    version = '1.0',
    description = 'SPI-Py: Hardware SPI as a C Extension for Python',
    license='GPL-v2',
    platforms=['Linux'],
    ext_modules = [module1]
)
