# *****************************************************************************
# * Copyright by ams OSRAM AG                                                 *
# * All rights are reserved.                                                  *
# *                                                                           *
# *FOR FULL LICENSE TEXT SEE LICENSES-MIT.TXT                                      *
# *****************************************************************************
"""
ZeroMQ server.
"""
import __init__
import logging
import time
import pathlib
import ctypes
import random
import zmq

from tmf8829_application_defines import *
from tmf8829_application_registers import Tmf8829_application_registers as Tmf8829AppRegs
from zeromq.tmf8829_host_com_reg import *
from tmf8829_config_page import Tmf8829_config_page as Tmf8829ConfigRegs


from tmf8829_application_common import Tmf8829AppCommon
from register_page_converter import RegisterPageConverter as RegConv

from zeromq.tmf8829_zeromq_common import *

LOG_FORMAT = '%(asctime)s %(message)s'
logging.basicConfig(level=logging.DEBUG,format=LOG_FORMAT)
logger = logging.getLogger(__name__)

class ZeroMqServer:
    """
    The Base class for a zeroMq-Server. provides a command and a data socket.
    """
    VERSION = 0x0003
    """Version 
    - 1 First zeromq server release version
    - 2 Second zeromq server release version
        SET_PRE_CONFIGURATION added
    - 3 Third zeromq server release version
        EVM Version reported
    """

    APPLICATION_ID = 0x01
    BOOTLOADER_ID = 0x80

    def __init__(self, use_spi=True, spi_mode=0, cmd_poll_interval=1.0) -> None:
        self._context = zmq.Context()
        if use_spi:
            self._speed = 15625000
        else:
            self._speed = 1000000

        self._cmd_socket = self._context.socket(zmq.REP)
        self._result_socket = self._context.socket(zmq.PUB)
        self._meas_running = False
        self.lost_results = 0  
        self._best_effort_results = False
        self._1st_client_id = TMF8829_ZEROMQ_CLIENT_NOT_IDENTIFIED
        self._cnt = 0
        self._cmd_poll_interval = cmd_poll_interval             # poll every xxx milliseconds for a new command
        self._last_cmd_poll = time.time() - cmd_poll_interval   # force a first poll
        self._newFrame()
        self._last_fnumber = 0
        self.nr_results = 0
        self._nr_subframes = 0

        random.seed()
        
        self.hostType = TMF8829_ZEROMQ_HOST_UNKNOWN 
        self.hostVersion = [0]*2
        self.hostVersion[0] = self.VERSION & 0xFF
        self.hostVersion[1] = (self.VERSION & 0xFF00) >> 8
        self.appVersion = [0]*4
        self.deviceSerialNumber = 0
        self.correctionFactor = 0
        self.romVersion = 0
        self.evm_version = EVM_VERSION


    # control socket == command handling ----------------------------------------

    def _process_CMD_request(self, request: Tmf8829zeroMQRequestMessage) -> Tmf8829zeroMQResponseMessage:
        """ Function that handles a single request message from the zMQ and returns the
        response message
        """
        _client_id = request.client_id

        try:
            logger.info("rcv {}".format(request.__str__()))              # print the received request first
            _error_code = Tmf8829zeroMQErrorCodes.NO_ERROR
            # Default response is to send 0x01 ( True ) 
            if int(Tmf8829zeroMQRequestId.IDENTIFY) == request.request_id:
                _device_info = self.identify()
                if _client_id == TMF8829_ZEROMQ_CLIENT_NOT_IDENTIFIED:
                    _client_id = random.randrange(1,0xFFFFFFFF)                           # new request from a new client
                if self._1st_client_id == TMF8829_ZEROMQ_CLIENT_NOT_IDENTIFIED:           # no first client, this is the one then
                    self._1st_client_id = _client_id
                if _client_id != self._1st_client_id:                                   
                    _error_code = Tmf8829zeroMQErrorCodes.NOT_CFG_CLIENT                               # additional info -> tell caller if they are config client or not
                resp = Tmf8829zeroMQResponseMessage(client_id=_client_id,error_code=_error_code, payload=_device_info)
            elif int(Tmf8829zeroMQRequestId.LEAVE) == request.request_id:
                if _client_id == self._1st_client_id:
                    self._1st_client_id = TMF8829_ZEROMQ_CLIENT_NOT_IDENTIFIED          # no first client, this is the one then
                    _p=b'\0x01'
                else:
                    _error_code=Tmf8829zeroMQErrorCodes.NOT_CFG_CLIENT
                    _p=b'\0x00'
                resp = Tmf8829zeroMQResponseMessage(client_id=_client_id,error_code=_error_code, payload=_p)
            elif _client_id != TMF8829_ZEROMQ_CLIENT_NOT_IDENTIFIED:
                if int(Tmf8829zeroMQRequestId.POWER_DEVICE) == request.request_id:
                    if _client_id == self._1st_client_id:
                        self.power_device()
                    else:
                        _error_code=Tmf8829zeroMQErrorCodes.NOT_CFG_CLIENT
                    resp = Tmf8829zeroMQResponseMessage(client_id=_client_id,error_code=_error_code, payload=self.deviceopen.to_buffer())
                elif int(Tmf8829zeroMQRequestId.START_MEASUREMENT) == request.request_id:
                    if _client_id == self._1st_client_id:
                        self.start_measurement()
                    else:
                        _error_code = Tmf8829zeroMQErrorCodes.NOT_CFG_CLIENT
                    if self._meas_running:  _p = b'\x01'    # measure status
                    else:                   _p = b'\x00'
                    resp = Tmf8829zeroMQResponseMessage(client_id=_client_id,error_code=_error_code, payload=_p)
                elif int(Tmf8829zeroMQRequestId.STOP_MEASUREMENT) == request.request_id:
                    if _client_id == self._1st_client_id:
                        self.stop_measurement()
                    else:
                        _error_code = Tmf8829zeroMQErrorCodes.NOT_CFG_CLIENT
                    if self._meas_running:  _p = b'\x01'    # measure status
                    else:                   _p = b'\x00'
                    resp = Tmf8829zeroMQResponseMessage(client_id=_client_id,error_code=_error_code,payload=_p)
                elif int(Tmf8829zeroMQRequestId.GET_CONFIGURATION) == request.request_id:
                    cfg = self.get_configuration()                      # read of configuration is possible for all clients!!!!!
                    if _client_id != self._1st_client_id: 
                        _error_code = Tmf8829zeroMQErrorCodes.NOT_CFG_CLIENT                        
                    resp = Tmf8829zeroMQResponseMessage(client_id=_client_id,error_code=_error_code, payload=cfg)
                elif int(Tmf8829zeroMQRequestId.SET_CONFIGURATION) == request.request_id:
                    if _client_id == self._1st_client_id:
                        self.set_configuration(request.payload)
                        resp = Tmf8829zeroMQResponseMessage(client_id=_client_id,error_code=_error_code,payload=b"\x01")
                    else:
                        resp = Tmf8829zeroMQResponseMessage(client_id=_client_id,error_code=Tmf8829zeroMQErrorCodes.NOT_CFG_CLIENT,payload=b"\x00")
                elif int(Tmf8829zeroMQRequestId.SET_PRE_CONFIGURATION) == request.request_id:
                    if _client_id == self._1st_client_id:
                        self.set_pre_config_cmd(request.payload)
                        resp = Tmf8829zeroMQResponseMessage(client_id=_client_id,error_code=_error_code,payload=b"\x01")
                    else:
                        resp = Tmf8829zeroMQResponseMessage(client_id=_client_id,error_code=Tmf8829zeroMQErrorCodes.NOT_CFG_CLIENT,payload=b"\x00")
                elif int(Tmf8829zeroMQRequestId.UPDATE_BINARIES) == request.request_id:
                    if _client_id == self._1st_client_id:
                        self.update_target_binaries(zip_blob=request.payload)
                        resp = Tmf8829zeroMQResponseMessage(client_id=_client_id,error_code=_error_code,payload=b"\x01")
                    else:
                        resp = Tmf8829zeroMQResponseMessage(client_id=_client_id,error_code=Tmf8829zeroMQErrorCodes.NOT_CFG_CLIENT,payload=b"\x00")
                else:
                    resp = Tmf8829zeroMQResponseMessage(client_id=_client_id,error_code=Tmf8829zeroMQErrorCodes.NOT_CFG_CLIENT,payload=b"\x00")
            else:
                raise Exception("Client must first request a client_id with command IDENTIFY") 
        except Exception as exc:
            logger.error(exc)
            resp = Tmf8829zeroMQResponseMessage(client_id=_client_id,error_code=Tmf8829zeroMQErrorCodes.ERROR)
        logger.info("send {}".format(resp.__str__()))              # print the received request first
        return resp

    # publisher socket == result frame handling -------------------------------------

    def _newFrame(self):
        """Function to reset internal structure for a new zeroMQ frame (result frames + histogram frames)"""
        self._result = bytearray()                              
        self._nr_subframes = 0
        self._res_fnumber = -1
        self._subs = [None]*2
        self._subs_fnumber = [None]*2

    def _removeIncompleteResults(self,result, fid, sub_idx, fnumber, raw_histograms):
        """Function checks if the result data is complete (this is only meaningful for non-blocking mode
            and for 32x32 or 48x32 modes where there are 2 result frames).
            In all other cases the results are always single frames and are complete.
        """
        if result:
            
            if raw_histograms == 0:            # not in blocking mode -> in blocking mode no frames can get lost
                if (fid & TMF8829_FID_MASK) == TMF8829_FID_RESULTS:
                    if sub_idx == 0:                    # just store the frame number
                        if self._res_fnumber != -1:     # duplicate result[0] without intermediate result[1] read
                            print( "WARNING missing sub-frame 1 in result, fnumber={}, expected={}".format(fnumber, self._last_fnumber+1))
                            self.lost_results += 1      # we missed one or more frame  
                            self._newFrame()            # discard all previous results stored,
                        elif (fnumber != self._last_fnumber + 1): # count missing frames for 8x8 and 16x16 modes
                            print( "missing frame(s) fnumber={}, expected={}".format(fnumber, self._last_fnumber+1))
                            self.lost_results += 1      # we missed one or more frame
                        self._res_fnumber = fnumber     # replace with this newly read sub-frame 0
                    elif sub_idx == 1:
                        if self._res_fnumber == -1 or self._res_fnumber != fnumber-1:
                            print( "WARNING missing sub-frame 1 and sub-frame 0 in result, fnumber={}, expected={}".format(fnumber, self._last_fnumber+1))
                            self._result = bytearray()  # discard all previous results stored
                            self.lost_results += 2      # we missed one or more frames  
                            self._newFrame()            # discard all previous results stored
                            result = None               # need to start collecting result frames again
            elif raw_histograms:
                if (fid & TMF8829_FID_MASK) == TMF8829_FID_RESULTS:
                    fpMode = fid & TMF8829_FPM_MASK
                    if (sub_idx == 0) and (fpMode <= Tmf8829AppCommon.FP_MODE_16x16):
                        if self._nr_subframes != (self.nr_results-1): # if nr_of_subframes not correct, frame(s) is (are) lost
                            print ("lost frame") 
                            self._result = bytearray()  # discard all previous results stored
                            self.lost_results += 1      # we missed one or more frames  
                            self._newFrame()            # discard all previous results stored
                            result = None               # need to start collecting result frames again
                    elif sub_idx == 1:
                        if self._nr_subframes != (self.nr_results-1): # if nr_of_subframes not correct, frame(s) is (are) lost
                            print ("lost frame")
                            self._result = bytearray()  # discard all previous results stored
                            self.lost_results += 1      # we missed one or more frames  
                            self._newFrame()            # discard all previous results stored
                            result = None               # need to start collecting result frames again


            self._last_fnumber = fnumber

        return result                         

    def _bestEffortResults(self, result, fid, sub_idx, fnumber, raw_histograms):
        """Function checks if the result data is complete (this is only meaningful for non-blocking mode
            and for 32x32 or 48x32 modes where there are 2 result frames).
            In all other cases the results are always single frames and are complete.
        """
        if result:
            if raw_histograms == 0:            # not in blocking mode -> in blocking mode no frames can get lost
                if (fid & TMF8829_FID_MASK) == TMF8829_FID_RESULTS:
                    if self.nr_results == 2:
                        if self._subs[sub_idx] != None:
                            print( "WARNING FNumber={} is missing missing sub[{}], one frame is lost".format(self._subs_fnumber[sub_idx],1-sub_idx))
                            self.lost_results += 1      # we missed one or more frame  
                        self._subs[sub_idx] = result            # keep a copy
                        self._subs_fnumber[sub_idx] = fnumber   # keep track which frame this is from
                        result = None                           # do not give back if there is only 1 sub-frame
                        if self._subs[0] != None and self._subs[1] != None:
                            self._nr_subframes += 1             # internally combine the 2 sub-frames so we need to add one here
                            result = self._subs[0] + self._subs[1]  # give back both at once.
                            #print( "Result Sub[0].FNumber={} Sub[1].FNumber={}".format(self._subs_fnumber[0], self._subs_fnumber[1]))
        return result                         


    
    def _readSingleResult(self, _readFrame, _readRefFrame):
        """Attempt to read in a result frame or (ref-result + result frame)
        Returns:
            list-of-frames, frame-ID, sub-frame-number, frame-number 
        """
        _result = bytearray()
        _sub = 0
        _fid = 0
        _fnumber = 0

        if _readFrame:
            _res_frame = bytearray(_readFrame)
            _size =Tmf8829AppCommon.PRE_HEADER_SIZE+ctypes.sizeof(struct__tmf8829FrameHeader)
            _header = tmf8829FrameHeader.from_buffer_copy( _res_frame[Tmf8829AppCommon.PRE_HEADER_SIZE:_size])
            _fid =_header.id
            
            if (_header.id & TMF8829_FID_MASK) == TMF8829_FID_RESULTS:                
                _sub = ( _header.layout >> Tmf8829AppCommon.RESULT_FRAME_SUBIDX_SHIFT ) & 1        # is 0 or 1 for results
            elif (_header.id & TMF8829_FID_MASK) == TMF8829_FID_HISTOGRAMS:
                _sub = _header.layout
            
            _fnumber = _header.fNumber
            _result += bytearray(_res_frame)
            #print( "Time={}, fnumber={}, sub={}".format(time.time(),_fnumber,_sub))
            if _readRefFrame:                                                    # ref frames + main result frame
                _result += bytearray(_readRefFrame)                                     
        return _result, _fid, _sub, _fnumber

    def _buildResultSet(self, result ):
        """ Function adds the zeroMQ header to the result frame """
        resheader = tmf8829ContainerFrameHeader()
        containerframe_size =  ctypes.sizeof(resheader)
        containerframe_payload = containerframe_size - 8 # remove Payload of Frame excluding previous 8 Bytes and payload Bytes
        resheader.magicNumber = TMF8829_ZEROMQ_PROTOCOL_MAGIC_NUMBER
        resheader.protocolVersion = TMF8829_ZEROMQ_PROTOCOL_VERSION
        resheader.payload = containerframe_payload + len(result)
        resheader.hostType = self.hostType
        resheader.deviceSerialNumber = self.deviceSerialNumber
        resheader.correctionFactor = self.correctionFactor
        result = bytearray(resheader) + result
        self._cnt += 1
        #print( "{} Complete sets".format(self._cnt) )
        return result

    # server start and server stop and server process --------------------------------------------------

    def start(self,cmd_addr: str = TMF8829_ZEROMQ_CMD_SERVER_ADDR,result_addr: str = TMF8829_ZEROMQ_RESULT_SERVER_ADDR) -> None:
        """
        Start the server
        Args:
            cmd_addr: Address for the command socket.
            result_addr: Address for the result socket.
        """
        logger.info("Server started.")
        self._open_communication_to_device()
        self._cmd_socket.bind(cmd_addr)
        self._result_socket.bind(result_addr)

    def stop(self) -> None:
        """
        Stop the server.
        """
        self._close_communication_to_device()
        self._cmd_socket.close()
        self._result_socket.close()
        self._context.term()
        logger.info("Server stopped")

    def process(self):
        """Function checks on both sockets if there are things to be done. """
        _time = time.time()
        if not self._meas_running or self._last_cmd_poll + self._cmd_poll_interval < _time: # when not running poll faster for commands
            if self._cmd_socket.poll(timeout=1) != 0:     # events queued within our time limit
                request = Tmf8829zeroMQRequestMessage(client_id=TMF8829_ZEROMQ_CLIENT_NOT_IDENTIFIED,buffer=self._cmd_socket.recv())
                logger.debug("Received: %s", request)
                response = self._process_CMD_request(request)
                logger.debug("Sending : %s", response)
                self._cmd_socket.send(response.to_buffer())

        if self._meas_running:
            self._process_results()


    # service routines to configure and communicate with the TMF8829 --------------------------------------
    def _process_results(self):
        raise NotImplementedError("Not implemented")

    def _open_communication_to_device(self) -> None:
        raise NotImplementedError("Not implemented")

    def _close_communication_to_device(self) -> None: 
        raise NotImplementedError("Not implemented")

    # ---- zeroMQ communication commands/response handling --------------------------------

    def identify(self) -> bytearray:
        """
        To sent the device information.
        Returns:
            Device information as a bytearray
        """
        logger.debug("Read device information")
        _dev_info = tmf8829ZmqDeviceInfo()
        ctypes.memset(ctypes.byref(_dev_info),0,ctypes.sizeof(tmf8829ZmqDeviceInfo))    # clear data first
        _dev_info.protocolVersion = TMF8829_ZEROMQ_PROTOCOL_VERSION                               # now fill data
        _dev_info.hostType = self.hostType
        for _ in range(2):
            _dev_info.hostVersion[_] = self.hostVersion[_]
        _dev_info.deviceSerialNumber = self.deviceSerialNumber
        for _ in range(4):
            _dev_info.fwVersion[_] = self.appVersion[_]
        for _ in range(8):
            _dev_info.evmVersion[_] = int.from_bytes(bytes=bytes(self.evm_version[_], "utf-8"),byteorder='little',signed=False)
        _buffer = ctypes.create_string_buffer(ctypes.sizeof(tmf8829ZmqDeviceInfo))
        ctypes.memmove(_buffer,ctypes.byref(_dev_info),ctypes.sizeof(tmf8829ZmqDeviceInfo))
        return _buffer.raw

    def power_device(self, on_off: bool) -> bool:
        """
        Power Device
        """
        logger.debug("Power Device")

        if(on_off):
            self._open_communication_to_device()
        else:
            self._close_communication_to_device()
        return on_off
    
    def start_measurement(self) -> bool:
        raise NotImplementedError("Not implemented")
    
    def stop_measurement(self) -> bool:
        raise NotImplementedError("Not implemented")

    def get_configuration(self) -> bytes:
        raise NotImplementedError("Not implemented")

    def set_configuration(self, configPagebytes:bytes) -> None:
        raise NotImplementedError("Not implemented")
 
    def set_pre_config_cmd(self, cmd:bytes) -> None:
        raise NotImplementedError("Not implemented")
    
    def update_target_binaries(self, zip_blob: bytes) -> None:
        raise NotImplementedError("Not implemented")
