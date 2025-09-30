# *****************************************************************************
# * Copyright by ams OSRAM AG                                                 *
# * All rights are reserved.                                                  *
# *                                                                           *
# *FOR FULL LICENSE TEXT SEE LICENSES-MIT.TXT                                 *
# *****************************************************************************
"""
ZeroMQ server for the tmf8829 linux driver
"""
from tmf8829_zeromq_server_core import *

from zipfile import ZipFile
from io import BytesIO
from pathlib import Path

import shutil
import subprocess

UPDATE_FOLDER = "/tmp/tmf8829/update"

### DRIVER ATTRIBUTES ###
DRIVER_PATH       = "/sys/class/i2c-adapter/i2c-0/0-0041/"

PROGRAM           = "tmf8829_common/program"
PROGRAM_VERSION   = "tmf8829_common/program_version"
REGISTERS         = "tmf8829_common/registers"
REGISTER_WRITE    = "tmf8829_common/register_write"
SERIAL_NUMBER     = "tmf8829_common/serial_number"

CONFIG_CUSTOM     = "tmf8829_app/config_custom"
CONFIG_MODE       = "tmf8829_app/config_mode"
START_MEASUREMENT = "tmf8829_app/start_measurement"
OUTPUT_DATA_NODE  = "tmf8829_app/app_tof_output"

MISC_DEVICE       = "/dev/tof_tmf8829"

PAGE_SIZE = 4096
TMF8829_FRAME_ID_RESULT    = 0xAA
TMF8829_FRAME_ID_HISTOGRAM = 0xBB

### Helper Functions ###

def read_from_misc_device(device_path):
    try:
        with open(device_path, 'rb') as device_file:
            data = device_file.read(PAGE_SIZE * 64)
            return data
    except IOError as e:
        print(f"Error reading from device: {e}")
        return None

### ZMQ Server Class ###

class ZeroMqLinuxServer(ZeroMqServer):
    """
    The server provides a command and a data socket. The command socket is bi-directional
    to allow to configure the device.
    The data socket provides unidirectional measurement results and optional histograms.
    Server for TMF8829 Linux Driver.
    """
    VERSION = 0x0001
    """Version 
    - 1 First zeromq server release version
    -
    """
    APPLICATION_ID = 0x01
    BOOTLOADER_ID = 0x80

    def __init__(self, cmd_poll_interval=1.0) -> None:
        super().__init__(cmd_poll_interval=cmd_poll_interval)
        self.fpMode = 0
        self.rawHistograms = 0
        self.dualMode = 0
        self.hostType = TMF8829_ZEROMQ_HOST_RASPBERRY_BOARD 


    def _process_results(self):
        """Function checks if measurements are ongoing. If they are it attempts to receive 
        result frames and adds this result to the internally stored result structure. As soon as 
        all result frames for one measurement are available an zeroMQ result-frame is published.
        """
        result_driver = read_from_misc_device(MISC_DEVICE)

        result_length = len(result_driver)
        if result_length == 0:
            time.sleep(0.001)
        else:
            data = list(result_driver)

            while (len(data) >= 8):
                driver_header = data[0:8]
                payload = driver_header[6] + driver_header[7] * 256
                frame = data[8:8+payload]
                data = data[8+payload:] # next frame if available
                
                #logger.debug("Header: {} Payload: {}".format( driver_header, payload ))

                if (driver_header[0] != TMF8829_FRAME_ID_RESULT) and (driver_header[0] != TMF8829_FRAME_ID_HISTOGRAM):
                    logger.debug(" No result or histogram frame,  fid: {}".format( driver_header[0]))
                    continue
                    
                result, fid, sub_idx, fnumber = self._readSingleResult(frame, None)  # Note: ref frame not implemented in linux driver
                if (fid & TMF8829_FID_MASK)  == TMF8829_FID_RESULTS:
                    self.correctionFactor = driver_header[2] + driver_header[3] * 256

                result = self._removeIncompleteResults(result, fid, sub_idx, fnumber, self.rawHistograms)

                if result:
                    self._result += result
                    self._nr_subframes += 1
                    if (self._nr_subframes == self.nr_results) and ((fid & TMF8829_FID_MASK)  == TMF8829_FID_RESULTS): # zeroMQ packet is complete (correct frame number and last frame is result frame)
                        res_to_send = self._buildResultSet( self._result )
                        self._result_socket.send(bytes(res_to_send))
                        self._newFrame()
                else:
                    logger.debug("Missing result frame.")

    # service routines to configure and communicate with the TMF8829 --------------------------------------
    def _open_communication_to_device(self) -> None:
        """
        Open the device connection.
        """
        logger.info( "Open communication with device")

        with open(DRIVER_PATH+PROGRAM_VERSION, encoding="utf-8") as f:
            values = f.read().strip().split()

        version = [ int(value, base=16) for value in values]
        self.appVersion = version
        
        logger.info( "Application={}.{}.{}.{}".format(version[0],version[1],version[2],version[3]))
     
        if version[0] == self.APPLICATION_ID:
            logger.debug(" Application is running")
        elif version[0] == self.BOOTLOADER_ID:
            logger.debug(" Bootloader is running")
        else:
            raise Exception("Wrong App, Failed to open device #2")

        self.deviceSerialNumber = self._get_serial_number()

    def _close_communication_to_device(self) -> None: 
        """
        Close the device connection.
        """
        logger.info("Close device connection.")
        
        self.stop_measurement()
        

    # ---- zeroMQ communication commands/response handling --------------------------------
    def start_measurement(self) -> bool:
        """
        Start measurement.
        """

        logger.debug("Enter Start measurement")
        self.nr_results = Tmf8829AppCommon.numberOfFrameReadsPerMeasurement(self.fpMode,self.rawHistograms,dualMode=self.dualMode)
        logger.info(" {} frames for a complete result set".format(self.nr_results))
        self._nr_subframes = 0
        self._result = bytearray()
        self._res_fnumber = -1
        self.lost_results = 0
        
        result = read_from_misc_device(MISC_DEVICE)
        logger.debug("Clear not send data: {}".format(len(result)))

        with open(DRIVER_PATH+START_MEASUREMENT, mode="w", encoding="utf-8") as f:
            values = f.write("1")
        
        self._meas_running = True
        logger.info("Result processing started.")
        return self._meas_running
            
    def stop_measurement(self) -> bool:
        """
        Stop measurement.
        """

        logger.debug("Stop measurement")

        with open(DRIVER_PATH+START_MEASUREMENT, mode="w", encoding="utf-8") as f:
            values = f.write("0")
        
        result = read_from_misc_device(MISC_DEVICE)
        logger.debug("Clear not send data: {}".format(len(result)))

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

        with open(DRIVER_PATH+CONFIG_CUSTOM, encoding="utf-8") as f:
            values = f.read().strip().split()
        
        configuration = [ int(value, base=16) for value in values]
        
        _cfg_dict = RegConv.readPageToDict(bytes(configuration),Tmf8829ConfigRegs())

        logger.info( _cfg_dict)
        self.fpMode =_cfg_dict["fp_mode"]
        self.rawHistograms =_cfg_dict["histograms"]
        self.dualMode = _cfg_dict["dual_mode"]

        return bytes(configuration)

    def set_configuration(self, configuration:bytes) -> None:
        """
        Set Configuration Page Data.
        Args:
            Bytes of Configuration Page.
        Raise:
            CommandError: Get Configuration failed
        """
        
        logger.debug("Set Device configuration")
        
        _cfg_dict = RegConv.readPageToDict(bytes(configuration),Tmf8829ConfigRegs())
        logger.info( _cfg_dict)
        self.fpMode =_cfg_dict["fp_mode"]
        self.rawHistograms =_cfg_dict["histograms"]
        self.dualMode = _cfg_dict["dual_mode"]

        values = " ".join(hex(e) for e in bytes(configuration))
        
        with open(DRIVER_PATH+CONFIG_CUSTOM, mode="w", encoding="utf-8") as f:
            values = f.write(values)

    def set_pre_config_cmd(self, cmd:bytes) -> None:
        """
        Set Pre configuration command
        Args:
            Bytes: pre configuration command.
        Raise:
            CommandError: Get Configuration failed
        """
        logger.debug("Set Device Pre configuration")

        values = " ".join(hex(e) for e in bytes(cmd))

        logger.debug("Num:" + values)


        with open(DRIVER_PATH+CONFIG_MODE, mode="w", encoding="utf-8") as f:
            values = f.write(values)


    def _get_serial_number(self) -> int:
        """ 
        Get the serial number of the device

        Returns:
            regs
        """

        with open(DRIVER_PATH+SERIAL_NUMBER, encoding="utf-8") as f:
            value = f.read()
        
        serial_number = int(value,base=16)

        logger.info("Serial Number: " + str(serial_number))

        return serial_number

    def update_target_binaries(self, zip_blob: bytes) -> None:
        """
        Update the EVM software like:

            - Sensor firmware
            - Linux driver
            - ZeroMQ server

        The needed files are zip as one file. The zip file must include one file
        with the name `update.py` in the root. This file must contain all instructions to
        update the related software components and restart the system if needed.
        On server side the zip file will be unzipped. And the `update.py` will be
        executed in a new process.

        Args:
            zip_blob: Zip file as byte blob.
        """
        logger.info("Update target binaries")
        update_folder = Path(UPDATE_FOLDER)
        if update_folder.exists():
            shutil.rmtree(update_folder) # cleanup
        update_folder.mkdir(parents=True, exist_ok=True)
        logger.debug("Created and cleaned update folder %s", update_folder)
        # Unzip
        with ZipFile(BytesIO(zip_blob)) as f:
            f.extractall(UPDATE_FOLDER)
        logger.debug("Files unzipped.")

        # Start update
        cmds = ["python3", "update.py"]
        subprocess.Popen(cmds, start_new_session=True, cwd=update_folder)
        logger.debug("Update process started.")


#####################################################################################
### ZERO MQ SERVER - MAIN                                                         ###
#####################################################################################

if __name__ == "__main__":
    import pathlib

    logging.basicConfig(level=logging.DEBUG,format='%(levelname)s %(name)s.%(funcName)s:%(lineno)d %(message)s')

    server = ZeroMqLinuxServer(cmd_poll_interval = 0.0001)
    server.start(cmd_addr= TMF8829_ZEROMQ_CMD_LINUX_SERVER_ADDR, result_addr=TMF8829_ZEROMQ_RESULT_LINUX_SERVER_ADDR)

    try:
        while True:
            server.process()
    except KeyboardInterrupt:
        pass

    server.stop()
