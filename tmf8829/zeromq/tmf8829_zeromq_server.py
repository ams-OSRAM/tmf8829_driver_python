# *****************************************************************************
# * Copyright by ams OSRAM AG                                                 *
# * All rights are reserved.                                                  *
# *                                                                           *
# *FOR FULL LICENSE TEXT SEE LICENSES-MIT.TXT                                 *
# *****************************************************************************
"""
ZeroMQ server.

EXE file creation:
Shield board zeromq server instantiation for server EXE file creation.
Run deploy_shield_board_zmq_server.py do deploy a server executable.

"""
import __init__

from zeromq.tmf8829_zeromq_server_core import *

from tmf8829_conv import *
from utilities.tmf8829_logger_service import TMF8829Logger as Tmf8829Logger
from tmf8829_application import Tmf8829Application

LOG_FORMAT = '%(asctime)s %(message)s'
logging.basicConfig(level=logging.ERROR)
#logging.basicConfig(level=logging.DEBUG,format=LOG_FORMAT)
logger = logging.getLogger(__name__)

class ZeroMqEVMServer(ZeroMqServer):
    """
    The server provides a command and a data socket. The command socket is bi-directional
    to allow to configure the device.
    The data socket provides unidirectional measurement results and optional histograms.
    """
    VERSION = 0x0003
    """Version 
    - 1 First zeromq server release version
    - 2 Second zeromq server release version
        SET_PRE_CONFIGURATION added
    - 3 Dual mode support 
    """

    APPLICATION_ID = 0x01
    BOOTLOADER_ID = 0x80

    def __init__(self,hex_file, use_spi=True, spi_mode=0, use_ram_app=True, cfg_dict=None, cmd_poll_interval=1.0) -> None:
        super().__init__(use_spi=use_spi,spi_mode=spi_mode,cmd_poll_interval=cmd_poll_interval)
        self.cfg_dict =cfg_dict
        self.app = createTmf8829( use_spi=use_spi, i2c_slave_addr=FRESNEL_I2C_ADDR, spi_mode= spi_mode)
        self._use_ram_app=use_ram_app
        self._use_spi = use_spi
        self.hostType = TMF8829_ZEROMQ_HOST_H5_BOARD 
        self._hex_file = hex_file


    # publisher socket == result frame handling -------------------------------------
 
    def _process_results(self):
        """Function checks if measurements are ongoing. If they are it attempts to receive a single
        result frame and adds this result to the internally stored result structure. As soon as 
        all result frames for one measurement are available an zeroMQ result-frame is published.
        """
        if self._meas_running:
            _readFrame, _readRefFrame = self.app.readFramesIfAvailable()
            result, fid, sub_idx, fnumber = self._readSingleResult(_readFrame, _readRefFrame) 
            if self._best_effort_results:
                result = self._bestEffortResults(result, fid, sub_idx, fnumber, self.app.cfg_histograms )
            else:   # only send complete result sets
                result = self._removeIncompleteResults(result, fid, sub_idx, fnumber, self.app.cfg_histograms)
            if result:
                self._result += result
                self._nr_subframes += 1
                if self._nr_subframes == self.nr_results:                   # zeroMQ packet is complete (all results + histograms)
                    res_to_send = self._buildResultSet( self._result )
                    self._result_socket.send(bytes(res_to_send))
                    logger.debug("Result frame sent.")
                    #print( "{} sent".format(fnumber))
                    self._newFrame()
    

    # service routines to configure and communicate with the TMF8829 --------------------------------------

    def writeConfigurationPage(self, config_data: bytearray) -> int:
        """Read the config page from the device change it and write it back.
        Args:
            config_data (bytearray): page to be written
        Returns:
            int - status of write
        """
        self.app.sendCommand( Tmf8829AppRegs.TMF8829_CMD_STAT._cmd_stat._CMD_LOAD_CONFIG_PAGE ) # load the config page.
        val = self.app.hal.tx([Tmf8829ConfigRegs.TMF8829_CFG_PERIOD_MS_LSB.addr],config_data)  # Now write the data via I2C.
        resp = self.app.sendCommand( Tmf8829AppRegs.TMF8829_CMD_STAT._cmd_stat._CMD_WRITE_PAGE )
        self.app.cfg_fpMode = (config_data[Tmf8829ConfigRegs.TMF8829_CFG_FP_MODE.addr-Tmf8829ConfigRegs.TMF8829_CFG_PERIOD_MS_LSB.addr]
                          & Tmf8829ConfigRegs.TMF8829_CFG_FP_MODE._fp_mode.mask) >> Tmf8829ConfigRegs.TMF8829_CFG_FP_MODE._fp_mode.shift
        self.app.cfg_resultFormat = config_data[Tmf8829ConfigRegs.TMF8829_CFG_RESULT_FORMAT.addr - Tmf8829ConfigRegs.TMF8829_CFG_PERIOD_MS_LSB.addr]
        self.app.cfg_histograms = (config_data[Tmf8829ConfigRegs.TMF8829_CFG_DUMP_HISTOGRAMS.addr-Tmf8829ConfigRegs.TMF8829_CFG_PERIOD_MS_LSB.addr] \
                              & Tmf8829ConfigRegs.TMF8829_CFG_DUMP_HISTOGRAMS._histograms.mask) >> Tmf8829ConfigRegs.TMF8829_CFG_DUMP_HISTOGRAMS._histograms.shift
        self.app.cfg_refFrame = (config_data[Tmf8829ConfigRegs.TMF8829_CFG_REF_SPAD_FRAME.addr-Tmf8829ConfigRegs.TMF8829_CFG_PERIOD_MS_LSB.addr]
                            & Tmf8829ConfigRegs.TMF8829_CFG_REF_SPAD_FRAME._publish.mask) >> Tmf8829ConfigRegs.TMF8829_CFG_REF_SPAD_FRAME._publish.shift
        self.app.cfg_dualMode = (config_data[Tmf8829ConfigRegs.TMF8829_CFG_ENABLE_DUAL_MODE.addr-Tmf8829ConfigRegs.TMF8829_CFG_PERIOD_MS_LSB.addr]
                            & Tmf8829ConfigRegs.TMF8829_CFG_ENABLE_DUAL_MODE._dual_mode.mask) >> Tmf8829ConfigRegs.TMF8829_CFG_ENABLE_DUAL_MODE._dual_mode.shift
        return resp[0]   # status only

    def _reset_device(self) -> None:
        version = list( self.hal.txRx( [0], 4 ) ) # read the first 4 bytes
        print("App={}.{}.{}.{}".format(version[0],version[1],version[2],version[3]))
        self.app.forceBootmonitor()
        version = list( self.hal.txRx( [0], 4 ) ) # read the first 4 bytes
        print("App={}.{}.{}.{}".format(version[0],version[1],version[2],version[3]))
        if version[0] == self.BOOTLOADER_ID:
            logger.debug("Device was reset ")
        else:
            raise Exception("Failed to reset device")

    def _open_communication_to_device(self) -> None:
        """
        Open the device connection.
        """
        if not self.app.open( speed=self._speed):
            raise Exception("ERROR no communication, exiting") 
        self.app.disable()
        time.sleep(0.03)
        self.app.enable(send_wake_up_sequence=False)
        
        if self._use_spi:
            self.app.blCmdI2cOff()                               # disable I2C interface to use pins for SWD
        else:
            self.app.blCmdSpiOff()                               # disable SPI interface to use pins for SWD

        version = list( self.app.hal.txRx( [0], 4 ) ) # read the first 4 bytes
        print("App={}.{}.{}.{}".format(version[0],version[1],version[2],version[3]))
        logger.info( "Open communication with device")
           
        if version[0] == self.APPLICATION_ID:
            logger.debug(" Application is running")
        elif version[0] == self.BOOTLOADER_ID:
            if self._use_ram_app:
                logger.debug("Ready to download application")
                self.app.downloadAndStartApp( hex_file=str(self._hex_file), use_fifo=True, verify=True )
                logger.debug("Start Ram App")
            else:
                logger.debug("Start Rom App")
                self.app.blCmdStartRomApp()

            version = list( self.app.hal.txRx( [0], 4 ) ) #for the download app not at 0x00 
            self.appVersion = version
            print( "App={}.{}.{}.{}".format(int(version[0]),int(version[1]),int(version[2]),int(version[3])))
            self.deviceSerialNumber = int.from_bytes(bytes=self.app.readSerialNumber(), byteorder="little", signed=False)
            self.romVersion = int.from_bytes(bytes=self.app.hal.txRx([0xE3],1), byteorder="little", signed=False )
            if version[0] == self.APPLICATION_ID:
                logger.debug("Application downloaded, Open Succeed")
            else:
                raise Exception("Wrong App, Failed to open device #1")
        else:
            raise Exception("Wrong App, Failed to open device #2")

        if self.cfg_dict:

            if "preconfig" in self.cfg_dict:
                pre_config = "_" +  self.cfg_dict["preconfig"]
                logger.debug("Preconfig {}".format(pre_config))
                precmd = getattr(Tmf8829AppRegs.TMF8829_CMD_STAT._cmd_stat, pre_config, None)
                self.app.sendCommand( cmd=precmd )

            _cfg_bytes = self.get_configuration()                                       # get configuration as a bytestream from device
            _cfg_dict = RegConv.readPageToDict(_cfg_bytes, Tmf8829ConfigRegs())         # convert bytestream to dictionary
            if "measure_cfg" in self.cfg_dict:
                Tmf8829Logger.patch_dict( _cfg_dict, self.cfg_dict["measure_cfg"] )    # external read config overwrites default config
                _cfg_bytes2 = RegConv.readDictToPage( _cfg_dict, Tmf8829ConfigRegs())   # bytearray
                self.set_configuration( _cfg_bytes2 )

    def _close_communication_to_device(self) -> None: 
        """
        Close the device connection.
        """
        logger.info("Close device connection.")
        self.app.stopMeasure()
        self.app.disable()
        self.app.close()

    # ---- zeroMQ communication commands/response handling --------------------------------
    def start_measurement(self) -> bool:
        """
        Start measurement.
        """
        logger.debug("Enter Start measurement")
        self.nr_results = self.app.numberOfFrameReadsPerMeasurement(fpMode=self.app.cfg_fpMode, \
                                                                    rawHistograms=self.app.cfg_histograms, \
                                                                    dualMode= self.app.cfg_dualMode)
        self._nr_subframes = 0
        self._result = bytearray()
        self._res_fnumber = -1        
        self.lost_results = 0
        resp = self.app.startMeasure()
        if resp[0] <= Tmf8829AppRegs.TMF8829_CMD_STAT._cmd_stat._STAT_ACCEPTED:
            logger.info( "Start measurement" )
        else:
            raise Tmf8829zeroMQRequestError("Failed to start measurement")
        self._meas_running = True
        logger.info("Result processing started.")
        return self._meas_running
            
    def stop_measurement(self) -> bool:
        """
        Stop measurement.
        """
        logger.debug("Stop measurement")
        resp = self.app.stopMeasure()
        if resp[0] == Tmf8829AppRegs.TMF8829_CMD_STAT._cmd_stat._STAT_OK:
            print( "Stop measurement" )
        else:
            raise Tmf8829zeroMQRequestError("Failed to stop measurement")
        self._meas_running = False
        self._nr_subframes = 0
        self._result = bytearray()
        logger.info("{} Result processing stopped.".format(time.time()))
        logger.info("Number lost result frames are at least {}".format(self.lost_results))
        self.lost_results = 0
        return self._meas_running

    def get_configuration(self) -> bytes:
        """
        Get Configuration Page Data
        Return:
            Bytes of Configuration Page.
        """
        logger.debug("Get Device configuration")
        config_data = self.app.loadConfig()
        return config_data

    def set_configuration(self, configPagebytes:bytes) -> None:
        """
        Set Configuration Page Data.
        Args:
            Bytes of Configuration Page.
        Raise:
            CommandError: Get Configuration failed
        """
        logger.debug("Set Device configuration")
        print( RegConv.readPageToDict(configPagebytes,Tmf8829ConfigRegs()))
        resp = self.writeConfigurationPage(configPagebytes)
        if resp != Tmf8829AppRegs.TMF8829_CMD_STAT._cmd_stat._STAT_OK:
            raise Tmf8829zeroMQRequestError("Failed to set Configuration")
 
    def set_pre_config_cmd(self, cmd:bytes) -> None:
        """
        Set Pre configuration command
        Args:
            Bytes: pre configuration command.
        Raise:
            CommandError: Get Configuration failed
        """
        logger.debug("Set Device Pre configuration")
                    
        resp = self.app.sendCommand(cmd= int(cmd[0]))
        if resp[0] != Tmf8829AppRegs.TMF8829_CMD_STAT._cmd_stat._STAT_OK:
            raise Tmf8829zeroMQRequestError("Failed to set Pre Configuration command")


if __name__ == "__main__":

    import sys

    if not isAmsEvmH5Available():
        print("Please connect an controller board.")
        input("Press Enter to continue...")
        exit(0)

    default_cfg = {
        "measure_cfg": {}
    }

    CONFIG_FILE = "./cfg_server.json"
    exe_hex = False
    # exe or script
    if getattr(sys, 'frozen', False): 
        script_location = sys.executable
        exe_hex = True
    else:
        script_location = os.path.abspath(__file__)

    script_location = os.path.dirname(script_location) 

    cfg_dict = Tmf8829Logger.readCfgFile(filePathName=script_location + CONFIG_FILE,in_config=default_cfg)

    logging.basicConfig(level=logging.DEBUG,format='%(levelname)s %(name)s.%(funcName)s:%(lineno)d %(message)s')
    
    if exe_hex:
        HEX_FILE = "./tmf8829_application.hex"
    else:
        from __init__ import HEX_FILE
        
    server = ZeroMqEVMServer( use_spi=True, cfg_dict=cfg_dict,hex_file=HEX_FILE)

    server.start()

    try:
        while True:
            server.process()
    except KeyboardInterrupt:
        pass

    server.stop()
