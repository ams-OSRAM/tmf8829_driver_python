# *****************************************************************************
# * Copyright by ams OSRAM AG                                                 *
# * All rights are reserved.                                                  *
# *                                                                           *
# *FOR FULL LICENSE TEXT SEE LICENSES-MIT.TXT                                 *
# *****************************************************************************
"""
"""

import __init__
import time
from aos_com.hal_register_io import HalRegisterIo
from tmf8829_host_regs import Tmf8829_host_regs as Tmf8829HostRegs

from aos_com.register_io import RegisterIo
from intelhex import IntelHex

class Tmf8829Device:
    """The TMF8829 device class.
    """
    
    VERSION = 1.0
    """Version log 
    - 1.0 First working version
    """

    def __init__(self, hal:HalRegisterIo, gpio_hal:HalRegisterIo=None ):
        """The default constructor. It initializes the FTDI driver.
        Args:
            hal (HalRegisterIo): The communication class instance to talk i2c or spi .
        """
        self.hal = hal
        if gpio_hal != None:
            self.gpio_hal = gpio_hal
        else:
            self.gpio_hal = hal
        self.reg = Tmf8829HostRegs()
        self.io = RegisterIo(ic_com=hal,log_level=RegisterIo.LOG_NONE)  # not so chatty
        self.is_open = False

    def open( self, speed:int=1000000) -> bool:
        """
        Open the communication.
        Args:
            speed (int, optional): Defaults to 1MHz.
        Returns:
            bool : True when successfully opened, else False
        """
        if self.hal.open(speed=speed) == self.hal.com._OK:
            if self.hal != self.gpio_hal:
                if self.gpio_hal.open( ) != self.gpio_hal.com._OK:
                    raise Exception("Failed to open I2C HAL for GPIOs")
            self.gpio_hal.com.gpioSetDirection( out_mask = self.gpio_hal.com.enable_pin, out_value = 0 )
            self.is_open = True
            return True
        return False
    
    def close( self ):
        """
        Closes the communication.
        """
        if self.is_open:
            self.hal.com.gpioSet( w_mask=self.gpio_hal.com.enable_pin, value=0 )
            if self.hal != self.gpio_hal:
                self.gpio_hal.close()       # close HAL for GPIO handling
            self.hal.close()
            self.is_open = False

    def enable(self, send_wake_up_sequence:bool = True) -> bool:
        """Enable the TMF882X.
        Args:
            send_wake_up_sequence (bool, optional): Send the power-on sequence for a cold start. Defaults to True.
        Returns:
            bool : True when successfully enabled / waked-up, else False
        """
        if self.is_open:
            self.gpio_hal.com.gpioSet(w_mask=self.gpio_hal.com.enable_pin, value=self.gpio_hal.com.enable_pin) 
            self.gpio_hal.com.gpioSet(w_mask=self.gpio_hal.com.enable_pin, value=self.gpio_hal.com.enable_pin) 
            time.sleep(0.003) # wait for 3 milliseconds until the device comes up.
            if send_wake_up_sequence:
                return self.wakeUp(powerup_select=Tmf8829HostRegs.ENABLE._powerup_select._FORCE_BOOTMONITOR)    #force boot monitor
            return True
        return False

    def isCpuReady(self, timeout:float=0.03) -> bool:
        """Wait for CPU to be """
        self.io.regRead( self.reg.ENABLE )
        if self.reg.ENABLE.pon:
            if self.reg.ENABLE.cpu_ready:
                return True                         # device is powered and awake, no need to enter waiting loop
            _max_time = time.time() + timeout
            while True:
                if self.isDeviceWakeup():
                    return True
                if time.time() > _max_time:
                    return False
        return False                    # device is not even powered, no sense in waiting 
    
    def isDeviceWakeup(self) -> bool:
        """Is cpu ready"""
        self.io.regRead( self.reg.ENABLE )
        if self.reg.ENABLE.pon and self.reg.ENABLE.cpu_ready:
            return True
        else:
            return False
        
    def reset(self):
        self.io.regWrite( self.reg.RESET, soft_reset=1 )    # this will put the device back in bootloader mode

    def forceBootmonitor(self):
        """Power down the TMF8829 in bootloader mode"""
        self.io.regWrite( self.reg.ENABLE, powerup_select=1, pon=1 )    # make sure device is powered
        self.reset()

    def wakeUp(self, powerup_select = Tmf8829HostRegs.ENABLE._powerup_select._RAM) -> bool:
        """wakeup up the TMF8829"""
        self.io.regWrite( self.reg.ENABLE, pon=1, powerup_select = powerup_select )  # request a power up = wakeup 
        time.sleep(0.003)                           # wait for 3 milliseconds until the device comes up.
        self.io.regRead( self.reg.ENABLE )          # read back
        if self.reg.ENABLE.cpu_ready:
            return True
        return False
    
    def gotoStandby(self) -> bool:
        """Power down the TMF8829"""
        if self.isDeviceWakeup():
            self.io.regWrite( self.reg.ENABLE, poff=1)  # request standby
            time.sleep(0.003)                           # wait for xx milliseconds until the device powers down
            self.io.regRead( self.reg.ENABLE )          # read again from HW to see new state
            if self.reg.ENABLE.cpu_ready == 0 and ( self.reg.ENABLE.standby_mode == 1 or  self.reg.ENABLE.timed_standby_mode == 1 ):
                return True
            return False
        return True

    def disable(self):
        """Disable the TMF8829"""
        if self.is_open:
            self.gpio_hal.com.gpioSet(w_mask=self.gpio_hal.com.enable_pin, value=0)

    def isIntPinPulledLow(self):
        """Check if the interrupt is pending, ie. if the INT pin is pulled low.
        Returns:
            bool: True if an interrupt is pending, False if it isn't 
        """
        if self.is_open:
            level = self.gpio_hal.com.gpioGet(r_mask=self.gpio_hal.com.interrupt_pin)
            return level == 0                                               # Open drain INT pin -> 0 == pending
        return False

    def readIntStatus(self) -> int:
        """ read the interrupt status register """
        self.io.regRead( self.reg.INT_STATUS )
        return self.io.get( self.reg.INT_STATUS )

    def clearIntStatus(self,bitMaskToClear):
        """ clear the interrupt status register 
         Args:
            bitMaskToClear: all bits set in this 8-bit mask will be cleared in the interrupt register 
        """
        self.io.regWrite( self.reg.INT_STATUS, val=bitMaskToClear )

    def readIntEnable(self) -> int:
        """ read the interrupt enable register """
        self.io.regRead( self.reg.INT_ENAB )
        return self.io.get( self.reg.INT_ENAB )
    
    def enableInt(self,bitMaskToEnable):
        """ enable all the interrupts that have the bit set in the parameter, all other interrupts will be disabled 
         Args:
            bitMaskToEnable: all bits set in this 8-bit mask will be enabled, all others disabled 
        """
        self.io.regWrite( self.reg.INT_ENAB, val=bitMaskToEnable )

    def clearAndEnableInt(self,bitMaskToEnable):
        """
        Clear and enable given interrupt bits
        Args:
            bitMaskToEnable : all bits set in this 8-bit mask will be cleared and enabled, all others disabled
        """
        self.clearIntStatus(bitMaskToEnable)    # first clear any old pending interrupt
        self.enableInt(bitMaskToEnable)         # now clear it
        
    def readAndClearInt(self,bitMaskToCheck):
        """
        Check if given interrupt bits are set, if they are, clear them and return them
        Args:
            bitMaskToCheck (TYPE): bit mask for interrupts to check for
        Returns:
            clr (TYPE): set interrupt bits that also have been cleared
        """
        clr = self.readIntStatus() & bitMaskToCheck
        if ( clr ):
            self.clearIntStatus( clr )
        return clr
    

class Tmf8829Bootloader(Tmf8829Device):
    """The TMF8829 bootloader class.
    """
    BL_READY                    = 0       #/*!< status success, ready to receive and execute next command */
    BL_ERR_PARAM                = 1       #/*!< last command had a parameter error, ready to receive and execute next command */
    BL_ERR_ADDR                 = 2       #/*!< last command tried to access RAM out of range, ready to receive and execute next command */
    BL_ERR_SIZE                 = 3       #/*!< last command had a size mismatch, ready to receive and execute next command */

    BL_MAX_DATA_SIZE            = 0x80

    BL_REG_CMD_STAT             = 0x08        #/*!< Host writes to this register the command, device writes to this register the status */
    BL_REG_SIZE                 = 0x09        #/*!< the size of the command or status response */
    BL_REG_DATA0                = 0x0A        #/*!< Data0 byte (can also be the checksum if no parameters are part of the command or status response */

    BL_REG_FIFO_STATUS          = 0xFE        #/*!< Fifo status location */ 
    BL_REG_FIFO                 = 0xFF        #/*!< Fifo location */ 

    # bootloader commands
    BL_CMD_START_RAM_APP        = 0x16
    BL_CMD_START_ROM_APP        = 0x17
    BL_CMD_DEBUG                = 0x18      # 3bytes total: 2 byte param cpu0, cpu1 
    BL_CMD_LOG                  = 0x19      # 3bytes total:2 byte param pin, log-level

    BL_CMD_SPI_OFF              = 0x20
    BL_CMD_I2C_OFF              = 0x22

    BL_CMD_R_RAM                = 0x40      # 2bytes total:1 byte param, length
    BL_CMD_W_RAM                = 0x41      # 2+bytes total:1+ byte param, length + values
    BL_CMD_W_RAM_BOTH           = 0x42      # 2+bytes total:1+ byte param, length + values
    BL_CMD_ADDR_RAM             = 0x43      # 5bytes total: 4 byte param, address

    BL_CMD_W_FIFO               = 0x44      # 1+4+2 bytes total: 4 +2 byte param, address, words
    BL_CMD_W_FIFO_BOTH          = 0x45      # 1+4+2 bytes total: 4 +2 byte param, address, words

    BL_CMD_R_HW                 = 0x80      # 5bytes total: 4 byte param, address 
    BL_CMD_W_HW                 = 0x81      # 9bytes total: 8 byte param, address + value (4bytes)
    BL_CMD_W_HW_MASK            = 0x82      # 13bytes total: 12 byte param, address + value (4bytes) + mask(4bytes)

    # how to select no-debugger shall be used for BL_CMD_DEBUG    
    BL_CMD_DEBUG__PARAM__NO_DEBUG       = 2

    BL_APP_ID   = 0x80          # the application ID of the bootloader
    APP_ID      = 0x01          # the application ID of the application

    VERSION = 1.0
    """Version log 
    - 1.0 First working version
    """
    def __init__(self, hal:HalRegisterIo, gpio_hal:HalRegisterIo=None ):
        """The default constructor. It initializes the FTDI driver.
        Args:
            hal (HalRegisterIo): The communication class instance to talk i2c or spi .
        """
        super().__init__(hal=hal,gpio_hal=gpio_hal)

    def _cmd( self, cmd:int, data:list, response_len:int=1 , timeout:float=1.0 ):
        """Function to execute a bootmonitor command
        Args:
            cmd(int): byte representing the command
            data(list): bytes to be transmitted with command (parameters)
            response_len(int): how many bytes shall be read as response (set to 0 if no response is expected). defaults to 1.
            timeout(float): how long to poll for a response, before giving up
        Return:
            list-of-bytes: the read-back response
        """
        if len(data):
            self.hal.tx( self.BL_REG_CMD_STAT, [ cmd, len(data) ] + data )
        else:
            self.hal.tx( self.BL_REG_CMD_STAT, [ cmd ] )
        if response_len > 0:
            _max_time = time.time() + timeout
            while True:
                _resp = self.hal.txRx(self.BL_REG_CMD_STAT, response_len )
                if _resp[0] != cmd or time.time() > _max_time:
                    return list(_resp)        # timeout, or response
        return [self.BL_READY]

    #--------------------------------------- bootmonitor functions -----------------------------
    def _blWaitForAppId( self, app_id=APP_ID, timeout:float=0.1):
        """Function waits for application to become available"""
        _max_time = time.time() + timeout
        while True:
            _data = self.hal.txRx( [0], 4 )         # read first 4 bytes of RAM should be app-id, app-version etc.
            if _data[0] == app_id:
                return _data
            elif time.time() > _max_time:
                assert app_id == _data[0], "Error application id expected ={}, but is={}".format(app_id, _data[0])

    def blCmdStartRamApp( self, app_id=APP_ID ):
        """Function executes command BL_CMD_START_RAM_APP"""
        _data = self._cmd( self.BL_CMD_START_RAM_APP, [], 10 )
        assert self.BL_ERR_PARAM != _data[0], "Error BL_CMD_START_RAM_APP: IVT[0] not pointing to RAM"
        assert _data[0] == self.BL_READY, "Error BL_CMD_START_RAM_APP: failed with status={}".format(_data[0])
        return self._blWaitForAppId(app_id=app_id )

    def blCmdStartRomApp( self ):
        """Function executes command BL_CMD_START_ROM_APP"""
        _data = self._cmd( self.BL_CMD_START_ROM_APP, [], 1 )
        assert self.BL_ERR_PARAM != _data[0], "Error BL_CMD_START_ROM_APP: IVT[0] not pointing to a valid RAM address (for stack)"
        return self._blWaitForAppId( )

    def blCmdDebug( self, cpu0 = BL_CMD_DEBUG__PARAM__NO_DEBUG, cpu1 = BL_CMD_DEBUG__PARAM__NO_DEBUG):
        """Function executes command BL_CMD_DEBUG"""
        assert cpu0 >= 0 and cpu0 <= 255
        assert cpu1 >= 0 and cpu1 <= 255
        _data = self._cmd( self.BL_CMD_DEBUG, [ cpu0, cpu1 ], 1 )
        assert _data[0] == self.BL_READY
        return _data

    def blCmdLog( self, pin, lvl ):
        """Function executes command BL_CMD_LOG"""
        assert pin >= 0 and pin <= 6
        assert lvl >= 0 and lvl <= 255
        _data = self._cmd( self.BL_CMD_LOG, [ pin, lvl ], 1 )
        assert _data[0] == self.BL_READY
        return _data

    def blCmdSpiOff( self ):
        """Function executes command BL_CMD_SPI_OFF"""
        _data = self._cmd( self.BL_CMD_SPI_OFF, [], 1 )
        assert _data[0] == self.BL_READY
        return _data

    def blCmdI2cOff( self ):
        """Function executes command BL_CMD_I2C_OFF"""
        _data = self._cmd( self.BL_CMD_I2C_OFF, [], 1 )
        assert _data[0] == self.BL_READY
        return _data

    def blCmdRRam( self, length:int ):
        """Function executes command BL_CMD_R_RAM"""
        _data = self._cmd( self.BL_CMD_R_RAM, [ length ], length+2 ) # +1 status, +1 size
        assert len(_data) == length+2
        assert _data[0] == self.BL_READY
        return _data

    def blCmdWRam( self, data:list ):
        """Function executes command BL_CMD_W_RAM"""
        _data = self._cmd( self.BL_CMD_W_RAM, data, 1 )
        assert _data[0] == self.BL_READY
        return _data

    def blCmdWRamBoth( self, data:list ):
        """Function executes command BL_CMD_W_RAM_BOTH"""
        _data = self._cmd( self.BL_CMD_W_RAM_BOTH, data, 1 )
        assert _data[0] == self.BL_READY
        return _data
    
    def blCmdAddrRam( self, addr:int ):
        """Function executes command BL_CMD_ADDR_RAM"""
        _addr = addr.to_bytes(length=4,byteorder='little',signed=False)
        _data = self._cmd( self.BL_CMD_ADDR_RAM, list(_addr), 1 )
        assert self.BL_READY == _data[0]
        return _data

    def _blCmdWFifo( self, cmd:int, addr:int, data:list ):
        """Function executes command BL_CMD_ADDR_RAM"""
        _addr = addr.to_bytes(length=4,byteorder='little',signed=False)
        _size = len(data)
        assert (_size//4)*4 == _size            # can only transfer words
        _size = _size//4 
        _size = _size.to_bytes(length=2,byteorder='little',signed=False)
        _resp = self._cmd( cmd, list(_addr) + list(_size), 1 )
        assert self.BL_READY == _resp[0]
        _status = self.hal.tx( self.BL_REG_FIFO, list(data) ) 
        assert _status == self.hal.com._OK

    def blCmdWFifo( self, addr:int, data:list ):
        """Function executes command BL_CMD_W_FIFO"""
        self._blCmdWFifo( self.BL_CMD_W_FIFO, addr, data )

    def blCmdWFifoBoth( self, addr:int, data:list ):
        """Function executes command BL_CMD_W_FIFO_BOTH"""
        self._blCmdWFifo( self.BL_CMD_W_FIFO_BOTH, addr, data )

    def blCmdRHw( self, addr ):
        """Function executes command BL_CMD_R_HW"""
        _addr = list( int.to_bytes( addr, length=4, byteorder='little', signed=False ) )
        _data = self._cmd( self.BL_CMD_R_HW, _addr, 6 )      # +1 status, +1 size, +4 data
        assert _data[0] == self.BL_READY
        return _data

    def blCmdWHw( self, addr, value ):
        """Function executes command BL_CMD_W_HW"""
        _addr = list( int.to_bytes( addr, length=4, byteorder='little', signed=False ) )
        _value = list( int.to_bytes( value, length=4, byteorder='little', signed=False ) )
        _data = self._cmd( self.BL_CMD_W_HW, _addr + _value, 1 )      
        assert _data[0] == self.BL_READY
        return _data

    def blCmdWHwMask( self, addr, value, mask ):
        """Function executes command BL_CMD_W_HW_MASK"""
        _addr = list( int.to_bytes( addr, length=4, byteorder='little', signed=False ) )
        _value = list( int.to_bytes( value, length=4, byteorder='little', signed=False ) )
        _mask = list( int.to_bytes( mask, length=4, byteorder='little', signed=False ) )
        _data = self._cmd( self.BL_CMD_W_HW_MASK, _addr + _value + _mask, 1 )      
        assert _data[0] == self.BL_READY
        return _data

    #--------------------------------------- convenience functions to download an image -----------

    def _downloadData(self, address:int, data: bytearray, use_fifo:bool, verify:bool) -> bool:
        """Load a data chunk to the target at a specific address.
        Args:
            address (int): The address on the target.
            data (bytearray): The data to be written onto the target. 
        Returns:
            True if download (and optional verify) were successfull, else returns False
        """
        if use_fifo:
            self.blCmdWFifoBoth( addr=address, data=list(data) )
        else:
            assert self.BL_READY == self.blCmdAddrRam( address )[0]
            for data_idx in range(0,len(data), self.BL_MAX_DATA_SIZE):
                _data = data[data_idx: data_idx + self.BL_MAX_DATA_SIZE]
                _data = list(_data)
                assert self.BL_READY == self.blCmdWRamBoth( _data )[0]
        if verify:
            assert self.BL_READY == self.blCmdAddrRam( address )[0]
            for data_idx in range(0,len(data), self.BL_MAX_DATA_SIZE):
                _data = data[data_idx: data_idx + self.BL_MAX_DATA_SIZE]
                _data = list(_data)
                _read = list(self.blCmdRRam( len(_data) )[2:] )
                assert _data == _read, "Data comparison failed on {}, offset {} :expected {} read {} ".format(hex(address), data_idx, _data, _read )
        return True
        
    def downloadHexFile(self, hex_file:str, use_fifo:bool, verify:bool) -> bool:
        """Download a application/patch hex file to the device.
           To run the application, call blCmdStartRamApp
        Args:
            hex_file (str): The firmware/patch to load.
            use_fifo (bool): select if upload should be done via FIFO or not.
            verify (bool): set to True to read-back and compare data
        Returns:
            True when successfully downloaded, else False
        """
        segments = []
        intel_hex = IntelHex()
        intel_hex.fromfile(hex_file, format='hex')
        segments = intel_hex.segments()
        assert len(segments) == 1, "Warning - Expecting only 1 segment, but found {}".format(len(segments))
        success = True
        for start_segment, end_segment in segments:
            print( "Loading image segment start: {:x}, end: {:x}".format(start_segment, end_segment))
            _data = intel_hex.tobinarray(start= start_segment, size= end_segment - start_segment)
            success = success and self._downloadData(start_segment, _data, use_fifo, verify)
        return success

    def downloadAndStartApp(self, hex_file:str, use_fifo:bool=False, verify:bool=True, app_id=APP_ID):
        """
        Convenience function: does download a hex file and start the downloaded applicaiton
        Args:
            hex_file (str): The firmware/patch to load.
            timeout (float, optional): Wait time in communication before give up. Defaults to 0.020.
        Returns:
            After successfull download returns the first 4 bytes from the device register map (e.g. I2C registers or SPI registers)
        """
        if self.downloadHexFile(hex_file,use_fifo,verify):
            if self.blCmdStartRamApp(app_id=app_id):
                self.io.regWrite( self.reg.ENABLE, powerup_select = self.reg.ENABLE._powerup_select._RAM )   # make sure a standby/standby-timed leads to proper reboot
                return list( self.hal.txRx( [0], 4 ) ) # read the first 4 bytes == app id etc.
        raise RuntimeError( "Download or Start of Application failed" )

if __name__ == "__main__":
    print("This program is not intended for standalone operation. Include it into application programs.")        
    from tmf8829_conv import *
    use_spi=False
    
    com = Host( log=False )
    if use_spi:
        from aos_com.spi_hal_register_io import SpiHalRegisterIo as Hal
        hal = Hal( ic_com=com, spi_mode=FRESNEL_SPI_MODE)
    else:
        from aos_com.i2c_hal_register_io import I2cHalRegisterIo as Hal
        hal = Hal( ic_com=com, dev_addr = FRESNEL_I2C_ADDR )

    fresnel = Tmf8829Bootloader( hal=hal)
    fresnel.open( )
    fresnel.enable(send_wake_up_sequence=False)
    assert fresnel.blCmdLog( 0, 255 )[0] == fresnel.BL_READY
    assert fresnel.blCmdLog( 6, 255 )[0] == fresnel.BL_READY

    for j in range(4):
        data = [7+_ for _ in range(0,128)]        # max is 128 bytes payload
        addr = 0x10000
        assert fresnel.blCmdAddrRam(addr)[0] == fresnel.BL_READY
        assert fresnel.blCmdWRam( data )[0] == fresnel.BL_READY
        assert fresnel.blCmdAddrRam(addr)[0] == fresnel.BL_READY
        read = fresnel.blCmdRRam( len(data) )
        if len(read) > 2:
            read = read[2:]
        assert len(read) == len(data)
        for i in range(0,len(read)):
            assert read[i] == data[i], "Error readback[{}]= {} expected {} ".format( i, hex(read[i]), hex(data[i])) 

        value = 0xFFFFFFFF
        assert fresnel.blCmdWHw( 0x10000, value )[0] == fresnel.BL_READY
        read = fresnel.blCmdRHw( 0x10000)
        read = int.from_bytes(read[2:], byteorder='little',signed=False)
        assert read == value

        old = value
        mask = 0x0FF000FF
        value = 0
        assert fresnel.blCmdWHwMask( 0x10000, value, mask )[0] == fresnel.BL_READY
        read = fresnel.blCmdRHw( 0x10000)
        read = int.from_bytes(read[2:], byteorder='little',signed=False)
        assert read == ( (old & ~mask) | ( value & mask ) )

    fresnel.disable( )
    fresnel.close()
