# *****************************************************************************
# * Copyright by ams OSRAM AG                                                 *
# * All rights are reserved.                                                  *
# *                                                                           *
# *FOR FULL LICENSE TEXT SEE LICENSES-MIT.TXT                                 *
# *****************************************************************************
"""
ZeroMQ common functions and classes.
"""
import logging
from enum import IntEnum
from typing import Optional
from zeromq.tmf8829_host_com_reg import *

logger = logging.getLogger(__name__)


class Tmf8829zeroMQProtocolError(Exception):
    """Command protocol error"""

class Tmf8829zeroMQRequestError(Exception):
    """Command error."""

class Tmf8829zeroMQRequestId(IntEnum):
    """Request command IDs."""
    NONE                  = 0x00
    IDENTIFY              = 0x01
    POWER_DEVICE          = 0x02 # Power Device
    LEAVE                 = 0x03 # when a client is no longer going to talk to the server it should send a leave request 
    START_MEASUREMENT     = 0x10
    STOP_MEASUREMENT      = 0x11
    GET_CONFIGURATION     = 0x20
    SET_CONFIGURATION     = 0x21
    SET_PRE_CONFIGURATION = 0x24
    UPDATE_BINARIES       = 0xA0 # Raspberry Pi Only

class Tmf8829zeroMQErrorCodes(IntEnum):
    """Error codes"""
    NO_ERROR       = 0x00  #: No error
    NOT_CFG_CLIENT = 0x01  #: Cannot reconfigure, as another client is first one
    SERVER_LOCK    = 0xfd  #  Server is locked for a command
    UNKNOWN_CMD    = 0xfe  #: Unknown command
    ERROR          = 0xff  #: Error

class Tmf8829zeroMQRequestMessage:
    """
    ZeroMQ request message.
    Args:
        client_id: the unique ID of this client. Provided by the server by an Identity request. reuse the
        one from the first time you requested one with Identify request
        request_id: request ID.
        payload: Message payload.
        buffer: Optional. Serialized request message.
    """

    def __init__(self, client_id, request_id=Tmf8829zeroMQRequestId.NONE, payload=b'', buffer: Optional[bytes] = None) -> None:
        self.request_id = request_id
        self.client_id = client_id
        self.payload = payload
        if buffer is not None:
            self.from_buffer(buffer)

    def __str__(self) -> str:
        return "Client=0x{:04x}: Req={} len={} data={}".format(self.client_id,Tmf8829zeroMQRequestId(self.request_id).name,len(self.payload),list(self.payload))

    def to_buffer(self) -> bytes:
        """
        Serialize the request message to byte buffer.
        Returns:
            Serialized request message.
        """
        return self.request_id.to_bytes(1, 'little') + self.client_id.to_bytes(length=4,byteorder="little",signed=False) + self.payload

    def from_buffer(self, buffer: bytes) -> None:
        """
        Recover the request from byte buffer.

        Args:
            buffer: Request message serialized as byte buffer.
        """
        self.request_id = buffer[0]
        self.client_id = int().from_bytes( bytes=buffer[1:5], byteorder="little", signed=False )                    
        self.payload = buffer[5:]


class Tmf8829zeroMQResponseMessage:
    """
    ZeroMQ response message.
    Args:
        client_id: the unique ID of this client. Provided by the server by an Identity request. 
        error_code: Error code.
        payload: Message payload as byte buffer.
        buffer: Optional. Serialized response message.
    Attributes:
        error_code (int): Error code.
        payload (bytes): Message payload.
    """

    def __init__(self, client_id, error_code=Tmf8829zeroMQErrorCodes.NO_ERROR, payload=b'', buffer: Optional[bytes] = None) -> None:
        self.client_id = client_id
        self.error_code = error_code
        self.payload = payload
        if buffer is not None:
            self.from_buffer(buffer)

    def __str__(self) -> str:
        return "Client=0x{:04x}: Rsp={} len={} data={}".format(self.client_id,Tmf8829zeroMQErrorCodes(self.error_code).name,len(self.payload),list(self.payload))

    def to_buffer(self) -> bytes:
        """
        Serialize the response message to byte buffer.
        Returns:
            Serialized response message.
        """
        return bytes([self.error_code]) + self.client_id.to_bytes(length=4,byteorder="little",signed=False) + self.payload

    def from_buffer(self, buffer: bytes) -> None:
        """
        Recover the response from byte buffer:
        Args:
            buffer: Response buffer serialized as byte buffer.
        """
        self.error_code = buffer[0]
        _client_id = int().from_bytes( bytes=buffer[1:5], byteorder="little", signed=False )
        if _client_id != self.client_id:
            print( "ClientId={}, received clientId={}".format(self.client_id, _client_id))
        self.client_id = _client_id                    
        self.payload = buffer[5:]
