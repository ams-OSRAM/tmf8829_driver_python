# *****************************************************************************
# * Copyright by ams OSRAM AG                                                 *
# * All rights are reserved.                                                  *
# *                                                                           *
# *FOR FULL LICENSE TEXT SEE LICENSES-MIT.TXT                                 *
# *****************************************************************************
"""
A set of convenience functions and imports.
"""

import __init__
import os
import corefw_c 

from aos_com.h5_com import isAmsEvmH5Available
from aos_com.h5_com import H5Com as Host

FRESNEL_I2C_ADDR=0x41
FRESNEL_SPI_MODE=0

# below defines are only valid when using the H5 board with the flat ribbon cable connector
TOF_GPIO0 = 1 << corefw_c.evm_h5.PioId.SPI1_MOSI
TOF_GPIO1 = 1 << corefw_c.evm_h5.PioId.SPI1_NSS
TOF_GPIO2 = 1 << corefw_c.evm_h5.PioId.SPI1_SCK
TOF_GPIO3 = 1 << corefw_c.evm_h5.PioId.SPI1_MISO                # only verified this one so far
TOF_GPIO4 = 1 << corefw_c.evm_h5.PioId.IXC2_SCL
TOF_GPIO5 = 1 << corefw_c.evm_h5.PioId.IXC2_SDA
TOF_GPIO6 = 1 << corefw_c.evm_h5.PioId.GPIO0

def createTmf8829( use_spi=True, i2c_slave_addr=FRESNEL_I2C_ADDR, spi_mode= 0, log=False):
    """Function creates the needed communication """
    import sys
    from tmf8829_application import Tmf8829Application
    
    print(sys.path)
    
    com = Host( log=log )
    if use_spi:
        from aos_com.spi_hal_register_io import SpiHalRegisterIo as Hal
        hal = Hal( ic_com=com, spi_mode=spi_mode)
    else:
        from aos_com.i2c_hal_register_io import I2cHalRegisterIo as Hal
        hal = Hal( ic_com=com, dev_addr = i2c_slave_addr )
    
    return Tmf8829Application( hal=hal, gpio_hal=hal )

