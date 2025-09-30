# *****************************************************************************
# * Copyright by ams OSRAM AG                                                 *
# * All rights are reserved.                                                  *
# *                                                                           *
# *FOR FULL LICENSE TEXT SEE LICENSES-MIT.TXT                                 *
# *****************************************************************************
"""
ZeroMQ client.
Start client and check for evm and shieldboard:
  - python .\tmf8829_zeromq_client.py
Start client and check for evm:
  - python .\tmf8829_zeromq_client.py evm
Start client and check for shieldboard:
  - python .\tmf8829_zeromq_client.py shieldboard
EXE file creation:
Shield board zeromq server instantiation for server EXE file creation.
Run deploy_shield_board_zmq_server.py do deploy a server executable.
"""
import __init__

import zmq
import ctypes
import time

from zeromq.tmf8829_zeromq_common import *

from tmf8829_application_registers import Tmf8829_application_registers as Tmf8829AppRegs
from tmf8829_config_page import Tmf8829_config_page as Tmf8829ConfigRegs
from aos_com.register_io import ctypes2Dict

class ZeroMqClient:
    """ZeroMQ client"""
   
    VERSION = 0x0003
    """Version 
    - 1 First zeromq client release version
    - 2 Second logger versions
        changes in logging format
    - 3 localhost and linuxhost check
        dual mode support
        point cloud correction
        version moved from client to logger
    - 4 option to save previous data also uncompressed (configuration changed at measurement)
        fix, check if filename exists also for gz files
        for storage use os pathname
    """

    def __init__(self) -> None:
        self._client_id = TMF8829_ZEROMQ_CLIENT_NOT_IDENTIFIED
        self._context = zmq.Context()
        self._cmd_socket = self._context.socket(zmq.REQ)
        self._result_socket = self._context.socket(zmq.SUB)
        self._is_measuring = False
        self._is_cfg_client = False
        self._cmd_socket.setsockopt(zmq.LINGER, 100) # after zmq close the Buffer should be cleared

    def connect_local(self):
        """Connect to local host server."""
        self._cmd_socket.connect(TMF8829_ZEROMQ_CMD_SERVER_ADDR)
        self._result_socket.connect(TMF8829_ZEROMQ_RESULT_SERVER_ADDR)
        self._result_socket.setsockopt(zmq.SUBSCRIBE, b'')
        logger.info("Connect to local host server")

    def disconnect_local(self):
        """Disconnect from local host server."""
        self._cmd_socket.disconnect(TMF8829_ZEROMQ_CMD_SERVER_ADDR)
        self._result_socket.disconnect(TMF8829_ZEROMQ_RESULT_SERVER_ADDR)
        logger.info("Disconnect from local host server")

    def connect_linux(self):
        """Connect to linux server."""
        self._cmd_socket.connect(TMF8829_ZEROMQ_CMD_LINUX_SERVER_ADDR)
        self._result_socket.connect(TMF8829_ZEROMQ_RESULT_LINUX_SERVER_ADDR)
        self._result_socket.setsockopt(zmq.SUBSCRIBE, b'')
        logger.info("Connect to linux server")

    def disconnect_linux(self):
        """Disconnect from linux server."""
        self._cmd_socket.disconnect(TMF8829_ZEROMQ_CMD_LINUX_SERVER_ADDR)
        self._result_socket.disconnect(TMF8829_ZEROMQ_RESULT_LINUX_SERVER_ADDR)
        logger.info("Disconnect from linux server")

    def send_request(
            self,
            request: Tmf8829zeroMQRequestMessage,
            request_timeout: float = 1.0,
            response_timeout: float = 1.0) -> Tmf8829zeroMQResponseMessage:
        """
        Send a request to the server and wait for response.
        Args:
            request: Request message to send.
            request_timeout: Timeout for sending the request message in seconds.
            response_timeout: Timeout for receiving the response message in seconds.
        Returns:
            Response message.
        Raises:
            CommandError: Request failed.
            TimeoutError: When a timeout elapsed before the request message was sent or before the response message was
                received.
        """
        request_timeout_ms = int(request_timeout * 1000.0)
        if not self._cmd_socket.poll(request_timeout_ms, zmq.POLLOUT):
            raise TimeoutError("Could not send request message")
        logger.info(request.__str__()) 
        self._cmd_socket.send(request.to_buffer())
        #Get the reply.
        response_timeout_ms = int(response_timeout * 1000.0)
        if not self._cmd_socket.poll(response_timeout_ms, zmq.POLLIN):
             raise TimeoutError("No response message received")
        response = Tmf8829zeroMQResponseMessage(client_id=self._client_id,buffer=self._cmd_socket.recv(copy=True))
        logger.info(response.__str__())
        if response.error_code == Tmf8829zeroMQErrorCodes.NO_ERROR :
            return response
        elif response.error_code == Tmf8829zeroMQErrorCodes.NOT_CFG_CLIENT :
            logger.debug("WARNING: not the 1st client of zeroMQ server, can only log")
            return response
        else:
            raise Tmf8829zeroMQRequestError("Host send request failed with {}".format(response.error_code))

    def identify(self) -> tmf8829ZmqDeviceInfo:
        """
        Identify the EVM controller and the target sensor. Get a new client_id if don't have one yet.
        Returns:
            Device information
        Raises:
            CommandError: Identify request failed.
        """
        resp = self.send_request(Tmf8829zeroMQRequestMessage(client_id=self._client_id,request_id=Tmf8829zeroMQRequestId.IDENTIFY))
        if self._client_id == TMF8829_ZEROMQ_CLIENT_NOT_IDENTIFIED:
            self._client_id = resp.client_id                                # store the newly given ID
        else:
            if self._client_id != resp.client_id:
                raise Tmf8829zeroMQRequestError("Identify, client-id={} differs from response itself={}".format(self._client_id,resp.client_id) )
        _device_info = tmf8829ZmqDeviceInfo.from_buffer_copy( resp.payload )
        if resp.error_code == Tmf8829zeroMQErrorCodes.NOT_CFG_CLIENT:
            self._is_cfg_client = False
            logger.info("ClientId={} Identify, LOGGER-ONLY client".format(self._client_id))
        else:
            self._is_cfg_client = True
            logger.info("ClientId={} Identify, CONFIG & LOGGER client".format(self._client_id))
        return _device_info

    def power_device(self, on_off: bytes) -> bool:
        """
        Power on or off the device.
        Args:
            on_off: 1 for on, 0 for off
        Returns:
            True: device is open
            False: device is closed
        """
        resp = self.send_request(Tmf8829zeroMQRequestMessage(client_id=self._client_id,request_id=Tmf8829zeroMQRequestId.POWER_DEVICE,payload=on_off))
        return bool(resp.payload[0])

    def leave(self) -> bool:
        """
        Release the client ID, if this was the Config-Client than another client can grab the config ID from the server.
        Returns:
            True: if client was config client
            False: if client was not the config client
        """
        resp = self.send_request(Tmf8829zeroMQRequestMessage(client_id=self._client_id,request_id=Tmf8829zeroMQRequestId.LEAVE))
        return bool(resp.payload[0])

    def start_measurement(self) -> bool:
        """
        Start measurement.
        Returns:
            True: if measurement is running
            False: else
        """
        resp = self.send_request(Tmf8829zeroMQRequestMessage(client_id=self._client_id,request_id=Tmf8829zeroMQRequestId.START_MEASUREMENT))
        self._is_measuring = bool(resp.payload[0])
        return self._is_measuring

    def stop_measurement(self) -> bool:
        """
        Stop measurement.
        Returns:
            True: if no measurement is running anymore (stop was successfully executed - or not running at all)
            False: measurement still ongoing 
        """
        resp = self.send_request(Tmf8829zeroMQRequestMessage(client_id=self._client_id,request_id=Tmf8829zeroMQRequestId.STOP_MEASUREMENT))
        self._is_measuring = bool(resp.payload[0])
        return self._is_measuring
    
    def get_config(self) -> bytes:
        """
        Get the configuration page data of the device.
        Returns:
            tmf8829 Configuration Registers data
        """
        resp = self.send_request(Tmf8829zeroMQRequestMessage(client_id=self._client_id,request_id=Tmf8829zeroMQRequestId.GET_CONFIGURATION))
        return resp.payload

    def set_config(self, config_page: bytes) -> bool:
        """
        Set the configuration page data of the device.
        Args:
            config_page: tmf8829 Configuration Registers data
        Returns:
            True: if request has been processed by command server
            False: else
        """
        resp = self.send_request(Tmf8829zeroMQRequestMessage(client_id=self._client_id,request_id=Tmf8829zeroMQRequestId.SET_CONFIGURATION,payload=config_page))
        return bool(resp.payload[0])

    def get_result_data(self, timeout: float = 5.0) -> bytes:
        """
        Read result data.
        Args:
            timeout: Timeout in seconds.
        Returns:
            Result data.
        Raises:
            TimeoutError: When no result data is received before the timeout elapsed.
        """
        timeout_ms = int(timeout * 1000.0)
        if not self._result_socket.poll(timeout_ms, zmq.POLLIN):
            raise TimeoutError("No result data received")
        result_data = self._result_socket.recv()

        return result_data

    def set_pre_config(self, cmd: bytes) -> bool:
        """
        Set the preconfigure command to the device.
        CMD_LOAD_CFG_8X8, CMD_LOAD_CFG_8X8_LONG_RANGE, CMD_LOAD_CFG_8X8_HIGH_ACCURACY, CMD_LOAD_CFG_16X16, CMD_LOAD_CFG_16X16_HIGH_ACCURACY,
        CMD_LOAD_CFG_32X32, CMD_LOAD_CFG_32X32_HIGH_ACCURACY, CMD_LOAD_CFG_48X32, CMD_LOAD_CFG_48X32_HIGH_ACCURACY

        Args:
            command : preconfigure command CMD_LOAD_CFG_8X8 ... CMD_LOAD_CFG_48X32_HIGH_ACCURACY

        Returns:
            True: if request has been processed by command server
            False: else (not the first client that requested)
        """
        
        resp = self.send_request(Tmf8829zeroMQRequestMessage(client_id=self._client_id,request_id=Tmf8829zeroMQRequestId.SET_PRE_CONFIGURATION, payload=cmd))

        return bool(resp.payload[0])
    
####################################################################

if __name__ == "__main__":
    from tmf8829_application_defines import *
    from tmf8829_application_common import Tmf8829AppCommon
    from utilities.tmf8829_logger_service import TMF8829Logger as Tmf8829Logger
    from register_page_converter import RegisterPageConverter as RegConv
    import sys
    import os

    debugMsg = False
    #####################################################
    ## Arguments 
    #####################################################
    use_linux_server = True
    use_shieldboard_server = True
    for arg in sys.argv[1:]:
        print ("arg: " + arg)
        if arg == "evm": # check only for linux server
            use_shieldboard_server = False
        if arg == "shieldboard": # check only for linux server
            use_linux_server = False
        break

    #####################################################
    ## CONFIGURATION - only valid if this client is 1st client for zeroMQ server 
    #####################################################
    default_client_cfg = {
        "measure_cfg": {},
        "logging": {"combined_results": True, "3d_correction": True },
        "record_frames":3
    }
    #####################################################
    CONFIG_FILE = "./cfg_client.json"
    if use_linux_server:
        CONFIG_FILE = "/cfg_client.json"
    
    # exe or script
    if getattr(sys, 'frozen', False): 
        script_location = sys.executable
    else:
        script_location = os.path.abspath(__file__)
        debugMsg = True
        
    script_location = os.path.dirname(script_location) 
   
    tmf8829logger = Tmf8829Logger()
    cfg = tmf8829logger.readCfgFile(filePathName=script_location + CONFIG_FILE, in_config=default_client_cfg)

    client = ZeroMqClient()
    localHostAvailable =False
    identify = False
    #####################################################
    # Local Host
    #####################################################
    if use_shieldboard_server:
        try:
            client.connect_local()
        except KeyboardInterrupt:
            print( "Exiting ... ")
            exit(0)

        # IDENTIFY - must be first command
        try:
            dev_info = client.identify()
            localHostAvailable =True
            identify = True
        except:
            localHostAvailable = False
            client.disconnect_local()
            print( "No connection to Shield board server !!!")
    
    #####################################################
    # Linux Host
    #####################################################
    if (localHostAvailable == False) and (use_linux_server == True):
        client = ZeroMqClient()
        try:
            client.connect_linux()
        except KeyboardInterrupt:
            print( "Exiting ... ")
            exit(0)
        try:
            dev_info = client.identify()
            identify = True
        except:
            client.disconnect_linux()
            print( "No connection to Evm board server !!!")
            time.sleep(2)
            exit(0)

    #####################################################
    if identify == False:
        exit(0)
    #####################################################

    print( "ClientID={}".format(client._client_id))
    print( ctypes2Dict(dev_info) )

    if "preconfig" in cfg:
        pre_config = "_" + cfg["preconfig"]
        logger.debug("Preconfig {}".format(pre_config))
        precmd = getattr(Tmf8829AppRegs.TMF8829_CMD_STAT._cmd_stat, pre_config, None)
        bprecmd =precmd.to_bytes(length=1,byteorder="little",signed=False)
        client.set_pre_config( cmd=bprecmd )

    # complete the user configuration with the device configuration
    _cfg_bytes = client.get_config()                                        # get configuration as a bytestream from device
    _cfg_dict = RegConv.readPageToDict(_cfg_bytes, Tmf8829ConfigRegs())     # convert bytestream to dictionary
    Tmf8829Logger.patch_dict( _cfg_dict, cfg["measure_cfg"] )               # external read config overwrites default config
    _cfg_bytes2 = RegConv.readDictToPage( _cfg_dict, Tmf8829ConfigRegs())   # bytearray
    client.set_config( _cfg_bytes2 )                                        # attempt to set configuration 
    _cfg_bytes = client.get_config()                                        # now in case we were not the 1st client, config might not have happened so read it back 
    _cfg_dict = RegConv.readPageToDict(_cfg_bytes, Tmf8829ConfigRegs())     # convert bytestream to dictionary
   
    tmf8829logger.dumpConfiguration( _cfg_dict )

    info = {}
    info["host version"] = list(dev_info.hostVersion)
    info["fw version"] = list(dev_info.fwVersion)
    info["logger version"] = client.VERSION
    info["serial number"] = dev_info.deviceSerialNumber
    tmf8829logger.dumpInfo(info)

    if _cfg_dict["select"] >= 1:
        print("The result frames have the distance in 0.25mm, but will be logged in mm! ")
    if cfg["logging"]["3d_correction"]:
        print("The result frames are point cloud corrected")

    if client.start_measurement():
        try:
            cnt = 0
            while cnt < cfg["record_frames"]:
                zmq_result_data = client.get_result_data()
                zmqheader = tmf8829ContainerFrameHeader.from_buffer_copy(bytearray(zmq_result_data[0:ctypes.sizeof(tmf8829ContainerFrameHeader)]))
                if debugMsg:
                    print( ctypes2Dict(zmqheader))
                    print("zmq Result Frames:")
                resultFrame, histoFrames, refFrame = Tmf8829AppCommon.getFramesFromMeasurementResult(zmq_result_data[ctypes.sizeof(tmf8829ContainerFrameHeader):])
                if debugMsg:
                    for r in resultFrame:
                            fpMode = r[5]&TMF8829_FPM_MASK  
                            fId = r[5]&TMF8829_FID_MASK
                            print( "FID={}, FP={}, FNr={}".format(fId, fpMode, int.from_bytes(bytes=r[5+4:5+4+4],byteorder='little', signed=False)))

                cnt += 1
                print( "Set={} #resultFrames={} #histoFrames={} #refFrames={}".format(cnt,len(resultFrame),len(histoFrames),len(refFrame)))
                if cfg["logging"]["combined_results"]:

                    _toMM = False
                    _3dCorr = False
                    if _cfg_dict["select"] >= 1:
                        _toMM = True
                    if cfg["logging"]["3d_correction"]:
                        _3dCorr = True
                    pixelResults = Tmf8829AppCommon.getFullPixelResult(frames=resultFrame, toMM=_toMM, pointCloud=_3dCorr, distanceToXYZ=True)

                    # log the header of the first result frame
                    fheader = tmf8829FrameHeader.from_buffer_copy( bytearray(resultFrame[0])[Tmf8829AppCommon.PRE_HEADER_SIZE: \
                              Tmf8829AppCommon.PRE_HEADER_SIZE+ctypes.sizeof(struct__tmf8829FrameHeader)])
                    ffooter = tmf8829FrameFooter.from_buffer_copy( bytearray(resultFrame[0])[-ctypes.sizeof(struct__tmf8829FrameFooter):])

                    res_info = {}
                    res_info["frame_number"] = fheader.fNumber
                    res_info["temperature"] = fheader.temperature[2]
                    res_info["systick_t0"] = ffooter.t0Integration
                    res_info["systick_t1"] = ffooter.t1Integration
                    res_info["read_time"] = int.from_bytes( resultFrame[0][1:5],byteorder='little',signed=False )
                    
                    allframeStatus = 0
                    for frame in histoFrames:
                        ffooter = tmf8829FrameFooter.from_buffer_copy( bytearray(frame)[-ctypes.sizeof(struct__tmf8829FrameFooter):])
                        allframeStatus |= ffooter.frameStatus
                    for frame in resultFrame:
                        ffooter = tmf8829FrameFooter.from_buffer_copy( bytearray(frame)[-ctypes.sizeof(struct__tmf8829FrameFooter):])
                        allframeStatus |= ffooter.frameStatus

                    res_info["warnings"] = allframeStatus & ~TMF8829_FRAME_VALID
                    
                    histogramResults = []
                    refhistogramResults = []
                    histogramResultsHA = []
                    refhistogramResultsHA = []     
                    
                    if _cfg_dict["histograms"] == 1:
                        if _cfg_dict["dual_mode"] == 1:
                            refhistogramResultsHA, histogramResultsHA, \
                            refhistogramResults, histogramResults = Tmf8829AppCommon.getAllHistogramResultsDualMode(histoFrames)
                        else:
                            refhistogramResults, histogramResults = Tmf8829AppCommon.getAllHistogramResults(histoFrames)
                    
                    tmf8829logger.dumpMeasurement(pixel_results=pixelResults, \
                        pixel_histograms=histogramResults, reference_pixel_histograms=refhistogramResults,
                        pixel_histograms_HA=histogramResultsHA, reference_pixel_histograms_HA=refhistogramResultsHA,
                        reference_spad_frames=refFrame, measurement_info=res_info)
                else:
                    for frame in histoFrames:
                        tmf8829logger.dumpFrame(frame)
                    for frame in resultFrame:
                        tmf8829logger.dumpFrame(frame)
                    for frame in refFrame:
                        tmf8829logger.dumpFrame(frame)

        except KeyboardInterrupt:
            pass
        except:
                tmf8829logger.dumpInfo({"Exception": "Get data from server"})
                print( "Exception:Get data from server  !!!!!!")
    else:
        print( "Only Logger and no measurement is running, exiting")

    try:
        client.stop_measurement()
        client.leave()  # if this client was config client free it again

        if localHostAvailable:
            client.disconnect_local()
        else:
            client.disconnect_linux()
    
    except:
        tmf8829logger.dumpInfo({"Exception": "Stop leave and disconnect from server"})
        print( "Exception: Stop Server !!!!!!")

    tmf8829logger.dumpToJsonFile(compressed=False)

    print( "End" )
    time.sleep(2)
