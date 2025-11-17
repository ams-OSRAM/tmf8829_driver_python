# *****************************************************************************
# * Copyright by ams OSRAM AG                                                 *
# * All rights are reserved.                                                  *
# *                                                                           *
# *FOR FULL LICENSE TEXT SEE LICENSES-MIT.TXT                                 *
# *****************************************************************************

import ctypes
from typing import List


class AsDictMixin:
    @classmethod
    def as_dict(cls, self):
        result = {}
        if not isinstance(self, AsDictMixin):
            # not a structure, assume it's already a python object
            return self
        if not hasattr(cls, "_fields_"):
            return result
        # sys.version_info >= (3, 5)
        # for (field, *_) in cls._fields_:  # noqa
        for field_tuple in cls._fields_:  # noqa
            field = field_tuple[0]
            if field.startswith('PADDING_'):
                continue
            value = getattr(self, field)
            type_ = type(value)
            if hasattr(value, "_length_") and hasattr(value, "_type_"):
                # array
                if not hasattr(type_, "as_dict"):
                    value = [v for v in value]
                else:
                    type_ = type_._type_
                    value = [type_.as_dict(v) for v in value]
            elif hasattr(value, "contents") and hasattr(value, "_type_"):
                # pointer
                try:
                    if not hasattr(type_, "as_dict"):
                        value = value.contents
                    else:
                        type_ = type_._type_
                        value = type_.as_dict(value.contents)
                except ValueError:
                    # nullptr
                    value = None
            elif isinstance(value, AsDictMixin):
                # other structure
                value = type_.as_dict(value)
            result[field] = value
        return result


class Structure(ctypes.Structure, AsDictMixin):

    def __init__(self, *args, **kwds):
        # We don't want to use positional arguments fill PADDING_* fields

        args = dict(zip(self.__class__._field_names_(), args))
        args.update(kwds)
        super(Structure, self).__init__(**args)

    @classmethod
    def _field_names_(cls):
        if hasattr(cls, '_fields_'):
            return (f[0] for f in cls._fields_ if not f[0].startswith('PADDING'))
        else:
            return ()

    @classmethod
    def get_type(cls, field):
        for f in cls._fields_:
            if f[0] == field:
                return f[1]
        return None

    @classmethod
    def bind(cls, bound_fields):
        fields = {}
        for name, type_ in cls._fields_:
            if hasattr(type_, "restype"):
                if name in bound_fields:
                    if bound_fields[name] is None:
                        fields[name] = type_()
                    else:
                        # use a closure to capture the callback from the loop scope
                        fields[name] = (
                            type_((lambda callback: lambda *args: callback(*args))(
                                bound_fields[name]))
                        )
                    del bound_fields[name]
                else:
                    # default callback implementation (does nothing)
                    try:
                        default_ = type_(0).restype().value
                    except TypeError:
                        default_ = None
                    fields[name] = type_((
                        lambda default_: lambda *args: default_)(default_))
            else:
                # not a callback function, use default initialization
                if name in bound_fields:
                    fields[name] = bound_fields[name]
                    del bound_fields[name]
                else:
                    fields[name] = type_()
        if len(bound_fields) != 0:
            raise ValueError(
                "Cannot bind the following unknown callback(s) {}.{}".format(
                    cls.__name__, bound_fields.keys()
            ))
        return cls(**fields)


class Union(ctypes.Union, AsDictMixin):
    pass





TMF8829_ZEROMQ_HOST_COM_REG_H = True # macro
TMF8829_ZEROMQ_PROTOCOL_VERSION = 2 # macro
TMF8829_ZEROMQ_PROTOCOL_MAGIC_NUMBER = 0xFE5E1234 # macro
TMF8829_ZEROMQ_CMD_SERVER_ADDR = "tcp://127.0.0.1:5557" # macro
TMF8829_ZEROMQ_RESULT_SERVER_ADDR = "tcp://127.0.0.1:5558" # macro
TMF8829_ZEROMQ_CMD_LINUX_SERVER_ADDR = "tcp://169.254.0.2:5557" # macro
TMF8829_ZEROMQ_RESULT_LINUX_SERVER_ADDR = "tcp://169.254.0.2:5558" # macro
TMF8829_ZEROMQ_CLIENT_NOT_IDENTIFIED = 0 # macro
TMF8829_ZEROMQ_HOST_UNKNOWN = 0 # macro
TMF8829_ZEROMQ_HOST_FTDI_BOARD = 1 # macro
TMF8829_ZEROMQ_HOST_ARDUINO_BOARD = 2 # macro
TMF8829_ZEROMQ_HOST_RASPBERRY_BOARD = 3 # macro
TMF8829_ZEROMQ_HOST_H5_BOARD = 4 # macro
TMF8829_ZEROMQ_HEADER_INFO_SIZE = 64 # macro
TMF8829_ZEROMQ_IDENTIFY_INFO_SIZE = 56 # macro
EVM_VERSION = "2.2.5   " # macro
class struct__tmf8829ZmqDeviceInfo(Structure):
    pass

class struct__tmf8829ZmqDeviceInfo(Structure):
    def __init__(self, *args):
        self.protocolVersion: ctypes.c_ubyte
        self.hostType: ctypes.c_ubyte
        """ 1 Byte; Protocol Version """
        self.hostVersion: List[ctypes.c_ubyte]
        """ FTDI = 1; Arduino = 2 Raspberry = 3, STMH5 = 4 """
        self.deviceSerialNumber: ctypes.c_uint32
        """ Host version """
        self.fwVersion: List[ctypes.c_ubyte]
        """ device serial number - little endian """
        self.evmVersion: List[ctypes.c_ubyte]
        """ FW version (appId/major), (minor), (patch), (capabilities) """
        self.info: List[ctypes.c_ubyte]
        """ EVM version """
        super().__init__(*args)
    _pack_ = 1
    _fields_ = [
    ('protocolVersion', ctypes.c_ubyte),
    ('hostType', ctypes.c_ubyte),
    ('hostVersion', ctypes.c_ubyte * 2),
    ('deviceSerialNumber', ctypes.c_uint32),
    ('fwVersion', ctypes.c_ubyte * 4),
    ('evmVersion', ctypes.c_ubyte * 8),
    ('info', ctypes.c_ubyte * 56),
     ]

tmf8829ZmqDeviceInfo = struct__tmf8829ZmqDeviceInfo
# A result container frame header
class struct__tmf8829ZmqContainerFrameHeader(Structure):
    pass

class struct__tmf8829ZmqContainerFrameHeader(Structure):
    """ A result container frame header """
    def __init__(self, *args):
        self.magicNumber: ctypes.c_uint32
        self.protocolVersion: ctypes.c_ubyte
        """ 4 Byte; Marker for Container frame 0xFE5E1234 """
        self.reserved: List[ctypes.c_ubyte]
        """ 1 Byte; Protocol Version """
        self.payload: ctypes.c_uint32
        self.hostType: ctypes.c_ubyte
        """ Payload of Frame excluding previous 8 Bytes and payload Bytes """
        self.reserved2: List[ctypes.c_ubyte]
        """ FTDI Adapter = 1; Arduino = 2 Raspberry = 3, STMH5 = 4 """
        self.correctionFactor: ctypes.c_uint16
        self.deviceSerialNumber: ctypes.c_uint32
        """ CLock Correction Factor Q1.15 for hostType = 3; 0 for not available """
        self.info: List[ctypes.c_ubyte]
        """ device serial number - little endian """
        super().__init__(*args)
    _pack_ = 1
    _fields_ = [
    ('magicNumber', ctypes.c_uint32),
    ('protocolVersion', ctypes.c_ubyte),
    ('reserved', ctypes.c_ubyte * 3),
    ('payload', ctypes.c_uint32),
    ('hostType', ctypes.c_ubyte),
    ('reserved2', ctypes.c_ubyte * 1),
    ('correctionFactor', ctypes.c_uint16),
    ('deviceSerialNumber', ctypes.c_uint32),
    ('info', ctypes.c_ubyte * 64),
     ]

tmf8829ContainerFrameHeader = struct__tmf8829ZmqContainerFrameHeader
__all__ = \
    ['EVM_VERSION', 'TMF8829_ZEROMQ_CLIENT_NOT_IDENTIFIED',
    'TMF8829_ZEROMQ_CMD_LINUX_SERVER_ADDR',
    'TMF8829_ZEROMQ_CMD_SERVER_ADDR',
    'TMF8829_ZEROMQ_HEADER_INFO_SIZE',
    'TMF8829_ZEROMQ_HOST_ARDUINO_BOARD',
    'TMF8829_ZEROMQ_HOST_COM_REG_H', 'TMF8829_ZEROMQ_HOST_FTDI_BOARD',
    'TMF8829_ZEROMQ_HOST_H5_BOARD',
    'TMF8829_ZEROMQ_HOST_RASPBERRY_BOARD',
    'TMF8829_ZEROMQ_HOST_UNKNOWN',
    'TMF8829_ZEROMQ_IDENTIFY_INFO_SIZE',
    'TMF8829_ZEROMQ_PROTOCOL_MAGIC_NUMBER',
    'TMF8829_ZEROMQ_PROTOCOL_VERSION',
    'TMF8829_ZEROMQ_RESULT_LINUX_SERVER_ADDR',
    'TMF8829_ZEROMQ_RESULT_SERVER_ADDR',
    'struct__tmf8829ZmqContainerFrameHeader',
    'struct__tmf8829ZmqDeviceInfo', 'tmf8829ContainerFrameHeader',
    'tmf8829ZmqDeviceInfo']
