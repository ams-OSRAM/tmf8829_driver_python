# *****************************************************************************
# * Copyright by ams OSRAM AG                                                 *
# * All rights are reserved.                                                  *
# *                                                                           *
# *FOR FULL LICENSE TEXT SEE LICENSES-MIT.TXT                                 *
# *****************************************************************************
"""
ZeroMQ server for the tmf8829 arduino driver
"""
from tmf8829_zeromq_server_core import *
from serial import Serial
from serial.tools import list_ports
from enum import Enum
from queue import Empty, Queue
from threading import Thread
from typing import  List
from time import sleep

### DRIVER ATTRIBUTES ###

class CommandError(Exception):
    """Command error."""

class Commands(Enum):
    """Arduino commands"""
    PRINT_REGISTER = b'a'  # Print all sensor register
    TOGGLE_CFG = b'c'  # Toggle sensor configuration
    DISABLE = b'd'  # Disable sensor
    ENABLE_WITH_FIRMWARE = b'e'  # Enable sensor download firmware and start RAM FW
    HELP = b'h'  # Print help
    START_MEAS = b'm'  # Start measurement
    STOP_MEAS = b's'  # Stop measurement
    PWR_DOWN = b'p'  # Power down sensor
    WAKE_UP = b'w'  # Wakeup sensor
    GET_CONFIGURATION = b'u'  # Get Configuration
    TOGGLE_CLK_CORR = b'x'  # Toggle clock correction on/off
    TOGGLE_HISTOGRAM_DUMP = b'z'  # Toggles the histogram to be dumped
    INC_LOG_LEVEL = b'+'  # Increase logging level
    DEC_LOG_LEVEL = b'-'  # Decrease logging level
    RESET = b'#'
    BINARY_MODE = b'b'
    BINARY_SET_CONFIG = b'\x31'  # Set arbitrary measurement configuration
    BINARY_SET_PRE_CONFIG = b'\x32'  # Set measurement pre-configuration
    BINARY_CHAR_MODE = b'\x00'  # Set the character mode

class FwStates(Enum):
    """Arduino firmware states"""
    DISABLED = b"disabled"
    STANDBY  = b"standby"
    STOPPED  = b"stopped"
    MEASURE  = b"measure"
    ERROR    = b"error"
    UNKNOWN  = b"UNKNOWN" # issue with connection 

class ResultId:
    """Identifier of result lines."""
    CONFIG   = b'#Config'
    DISTANCE = b"#Obj"
    ERROR    = b"#Err"

class ZeroMqArduinoServer(ZeroMqServer):
    """
    The server provides a command and a data socket. The command socket is bi-directional
    to allow to configure the device.
    The data socket provides unidirectional measurement results and optional histograms.
    Server for TMF8829 Arduino Driver.
    """
    VERSION = 0x0001
    """Version 
    - 1 First zeromq server release version
    -
    """
    APPLICATION_ID = 0x01
    BOOTLOADER_ID = 0x80

    def __init__(self, port: str, cmd_poll_interval=1.0, baudrate=2000000) -> None:
        super().__init__(cmd_poll_interval=cmd_poll_interval)
        
        self._com = Serial(baudrate=baudrate, timeout=0.1)
        self._com.port = port
        self._cmd_resp_lines = Queue()
        self._read_thread: Optional[Thread] = None
        self._abort = False
        self.fpMode = 0
        self.rawHistograms = 0
        self.hostType = TMF8829_ZEROMQ_HOST_ARDUINO_BOARD
        self._result_object = bytearray()

    @staticmethod
    def print_connected_com_ports():
        """
        print connected com ports
        """
        ports = list_ports.comports()
        for port in ports:
            print(f"Com Port Device: {port.device}, Description: {port.description}, HWID: {port.hwid}")
        return

    @staticmethod
    def device_connected(dev="Uno") -> List[str]:
        """
        Return a list of devices that are connected.
        Args:
          dev: "Uno" for Arduino Uno,"Zero" for Arduino Zero; other devices not implemented 
        Returns:
            List[str]: list ports
        """
        dl = []
        if dev == "Uno":
            dl = [e.name for e in list_ports.grep(r"USB VID:PID=2341.*")]
        elif dev == "Zero":
            dl = [e.name for e in list_ports.grep(r"USB VID:PID=03EB:2157*")]
        else:
            logging.info("device search not implemented")
            
        return dl
    
    def _clear_queue(self, queue: Queue) -> None:
        """
        Discard all queue items.

        Args:
            queue: Queue to clear.
        """
        while queue.not_empty:
            try:
                queue.get_nowait()
            except Empty:
                break

    def _process_input_data(self):
        """Read data from the serial port and process them."""
        try:
            while not self._abort:
                line = self._com.readline().strip()
                if line:
                    # logger.debug("->: %s", line)
                    if line.startswith(ResultId.CONFIG):
                        self._cmd_resp_lines.put(line)
                    elif line.startswith(ResultId.DISTANCE):
                        values = line.split()[-1].split(b',')
                        result_driver = []
                        for val in values:
                            if val != b'':
                                result_driver.append(int(val,base=10))
                        self._result_object = bytearray(result_driver)
                        #logger.debug(" _process_input_data: {}".format(len(self._result_object)))
                    elif line.startswith(ResultId.ERROR):
                        self._cmd_resp_lines.put(line)
                    elif line.startswith(b'#'):
                        pass
                    else:
                        self._cmd_resp_lines.put(line)

        except Exception as exc:
            logger.error(exc)

    def _send_command(self,
                      command: Commands,
                      payload: Optional[bytes] = None,
                      expected_state: Optional[FwStates] = None) -> List[bytes]:
        """
        Send a command to the device and read the response.

        Args:
            command: Command to send

            payload: Optional command payload. Defaults to None.

            expected_state: Expected firmware state after command execution.
                The returned state is ignored if `None`.

        Raises:
            CommandError: The responded device state is 'error'.

        Returns:
            Command response.
        """
        self._clear_queue(self._cmd_resp_lines)
        logger.debug("<-: %s", command.value)
        self._com.write(command.value)
        if payload is not None:
            logger.debug("<-: %s", " ".join(f"0x{e:02x}" for e in payload))
            self._com.write(payload)
        
        resp_finished = False
        response = []
        while not resp_finished:
            item =self._cmd_resp_lines.get(block=True, timeout=4.0)
            response.append(item)
            if response[-1].startswith(b"state="):
                state = FwStates(response[-1].split(b"=", 1)[-1])
                logger.debug("Actual state: %s", state)
                if expected_state == state or expected_state is None:
                    resp_finished = True
                elif state == FwStates.ERROR:
                    raise CommandError("Device in ERROR state.")
            elif response[-1].startswith(ResultId.ERROR):
                raise CommandError(f"Command error: {response[-1]}")
        return response
    
    def _process_results(self):
        """Function checks if measurements are ongoing. If they are it attempts to receive 
        result frames and adds this result to the internally stored result structure. As soon as 
        all result frames for one measurement are available an zeroMQ result-frame is published.
        """
        if (self._meas_running) and ( len(self._result_object) >= 1 ):

            frame = self._result_object

            result, fid, sub_idx, fnumber = self._readSingleResult(frame, None) 

            logger.debug("frame number: {} with len {}".format(fnumber, len(self._result_object)))
            self._result_object = bytearray()

            result = self._removeIncompleteResults(result, fid, sub_idx, fnumber, self.rawHistograms)

            if result:
                self._result += result
                self._nr_subframes += 1
                #logger.debug("one subset _nr_subset {} nr_results {}".format(self._nr_subframes,self.nr_results ))
                # zeroMQ packet is complete (all results + histograms)
                if self._nr_subframes == self.nr_results:  
                    res_to_send = self._buildResultSet( self._result )
                    self._result_socket.send(bytes(res_to_send))
                    logger.debug("Result Set send")
                    self._newFrame()

    # service routines to configure and communicate with the TMF8829 
    def _open_communication_to_device(self) -> None:
        """
        Open the device connection.
        """
        logger.info( "Open communication with device")
        
        self._com.open()
        self._abort = False
        self._read_thread = Thread(target=self._process_input_data, name="Arduino serial reader")
        self._read_thread.start()
        sleep(2.0)  # Wait of arduino firmware startup.
        try:
            logger.info( "Enable the device")
            for line in self._send_command(Commands.ENABLE_WITH_FIRMWARE, expected_state=FwStates.STOPPED):
                if line.startswith(b"CPU ready"): #just an info
                     pass              
                elif line.startswith(b"TMF8829 Arduino Driver Version "):
                    version = line.split(b" ")[-1].split(b'.')
                elif line.startswith(b"Firmware Application Version "):
                    version = line.split()[-1].split(b'.')
                    for _ in range(4):
                        self.appVersion[_] = int(version[_])
                elif line.startswith(b"Chip Version "):
                    pass
                elif line.startswith(b"Serial Number "):
                    self.deviceSerialNumber = int(line.split(b" ")[-1], 16)
                elif line.startswith(b"state"):
                    state = line.split(b"=")[1]
            self._send_command(Commands.INC_LOG_LEVEL, expected_state=FwStates.STOPPED)
            sleep(0.1)
        except Exception as exc:
            logger.info("Could not enable the device")
            sleep(0.1)
            self._close_communication_to_device()


    def _close_communication_to_device(self) -> None: 
        """
        Close the device connection.
        """
        logger.info("Close device connection.")

        try:
            self._send_command(Commands.DISABLE, expected_state=FwStates.DISABLED)
        except Exception:
            logger.info("Could not disable.")

        self._com.close()
        

    def _reopen_communication_to_device(self) -> None: 
        """
        Reopen the device connection.
        """
        logger.info("--XXX Reopen device connection. XXX--")
        
        self._com.close()
        sleep(0.1)
        self._open_communication_to_device()


    # ---- zeroMQ communication commands/response handling --------------------------------
    def start_measurement(self) -> bool:
        """
        Start measurement.
        """

        logger.debug("Enter Start measurement")
        self.nr_results = Tmf8829AppCommon.numberOfFrameReadsPerMeasurement(self.fpMode,self.rawHistograms)
        logger.debug(" {} frames for a complete result set".format(self.nr_results))
        self._nr_subframes = 0
        self._result = bytearray()
        self._result_object = bytearray()
        self._res_fnumber = -1
        self.lost_results = 0
        
        try:
            self._send_command(Commands.START_MEAS)
        except Exception as exc:
            logger.info("Could not start the measurement.")
            sleep(0.1)
            self._reopen_communication_to_device()

        self._meas_running = True
        logger.info("Result processing started.")
        return self._meas_running
            
    def stop_measurement(self) -> bool:
        """
        Stop measurement.
        """

        logger.debug("Stop measurement")
        state = FwStates.STOPPED.value
        try:
            for line in self._send_command(Commands.STOP_MEAS):
                if line.startswith(b"state"):
                    state = line.split(b"=")[1]             
        except Exception as exc:
            state = FwStates.UNKNOWN.value

        self._meas_running = False
        self._nr_subframes = 0
        self._result = bytearray()
        self.lost_results = 0

        if state == FwStates.STOPPED.value:
          logger.info("{} Result processing stopped.".format(time.time()))
          logger.info("Number lost result frames are at least {}".format(self.lost_results))
        else:
            logger.info("Stop the measurement FAILED. Re-open com!!!")
            self._reopen_communication_to_device

        return self._meas_running

    def get_configuration(self) -> bytes:
        """
        Get Configuration Page Data
        Return:
            Bytes of Configuration Page.
        """

        logger.debug("Get Device configuration")
        values = []
        configuration = []
        try:
            for line in self._send_command(Commands.GET_CONFIGURATION):
                if line.startswith(b"#Config"):
                    values = line.split()[-1].split(b',')
                else:
                    pass
                
            for val in values:
                if val != b'':
                    configuration.append(int(val,base=16))
            
            if len(configuration) >=1:
                _cfg_dict = RegConv.readPageToDict(bytes(configuration),Tmf8829ConfigRegs())
                logger.info( _cfg_dict)
                self.fpMode =_cfg_dict["fp_mode"]
                self.rawHistograms =_cfg_dict["histograms"]
            else:
                logger.info("Could not read the configuration")
        except Exception as exc:
            logger.info("Could not read the configuration")
            sleep(0.1)
            self._reopen_communication_to_device()

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

        try:
            self._send_command(Commands.BINARY_MODE)
            for line in self._send_command(Commands.BINARY_SET_CONFIG, configuration):
                if line.startswith(b"Binary input mode inactive"):
                    pass
                else:
                    pass
                
            _cfg_dict = RegConv.readPageToDict(bytes(configuration),Tmf8829ConfigRegs())
            logger.info( _cfg_dict)
            self.fpMode =_cfg_dict["fp_mode"]
            self.rawHistograms =_cfg_dict["histograms"]

        except Exception as exc:
            logger.info("Could not set the configuration")
            sleep(0.1)
            self._reopen_communication_to_device()

        sleep(0.1)

    def set_pre_config_cmd(self, cmd:bytes) -> None:
        """
        Set Pre configuration command
        Args:
            Bytes: pre configuration command.
        Raise:
            CommandError: Get Configuration failed
        """
        logger.debug("Set Device Pre configuration")
        
        try:
            self._send_command(Commands.BINARY_MODE)
            for line in self._send_command(Commands.BINARY_SET_PRE_CONFIG, cmd):
                if line.startswith(b"Binary input mode inactive"):
                    pass
                else:
                    pass
        except Exception as exc:
            logger.info("Could not set the pre configuration")
            sleep(0.1)
            self._reopen_communication_to_device()

        sleep(0.1)

#####################################################################################
### ZERO MQ SERVER - MAIN                                                         ###
#####################################################################################

if __name__ == "__main__":

    BAUDRATE=2000000

    logging.basicConfig(level=logging.DEBUG,format='%(levelname)s %(name)s.%(funcName)s:%(lineno)d %(message)s')
    ZeroMqArduinoServer.print_connected_com_ports()

    com_port = ZeroMqArduinoServer.device_connected()
    
    if len(com_port) >= 1: 
        logging.info("Arduino Uno Board found Com {}".format(com_port[0]))
    else:
        logging.info("No Arduino Uno Board found")
        com_port = ZeroMqArduinoServer.device_connected("Zero")
        BAUDRATE=1000000

    if len(com_port) >= 1: 
        server = ZeroMqArduinoServer(port= com_port[0], cmd_poll_interval = 0.01, baudrate=BAUDRATE)
        server.start(cmd_addr= TMF8829_ZEROMQ_CMD_SERVER_ADDR, result_addr=TMF8829_ZEROMQ_RESULT_SERVER_ADDR)
        try:
            while True:
                server.process()
        except KeyboardInterrupt:
            pass

        server.stop()

    else:
        logging.info(" No Board found")
