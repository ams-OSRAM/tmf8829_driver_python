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


TMF8829_APPLICATION_CAPABILITIES = 0x00 # macro
TMF8829_APPLICATION_MINOR = 0x07 # macro
TMF8829_APPLICATION_MAJOR = 0x02 # macro
TMF8829_APPLICATION_ID = 0x01 # macro
TMF8829_INT_HISTOGRAMS = 0x08 # macro
TMF8829_INT_RESULTS = 0x01 # macro
TMF8829_FID_MASK = 0xF0 # macro
TMF8829_FPM_MASK = 0x0F # macro
TMF8829_FID_RESULTS = 0x10 # macro
TMF8829_FID_HISTOGRAMS = 0x20 # macro
TMF8829_FID_REF_SPAD_SCAN = 0x30 # macro
TMF8829_FRAME_VALID = 0x01 # macro
TMF8829_FRAME_ABORTED = 0xC0 # macro
TMF8829_FRAME_WARNING_HV_CP_OVERLOAD = 0x08 # macro
TMF8829_FRAME_WARNING_VCDRV_OVERLOAD = 0x10 # macro
TMF8829_FRAME_WARNING_VCDRV_BURST_EXCEEDED = 0x20 # macro
TMF8829_FRAME_EOF = 0xE0F7 # macro
TMF8829_MAX_PEAKS_PER_MP = 4 # macro
TMF8829_FRAME_HEADER_OFFSET = 4 # macro
TMF8829_FRAME_HEADER_SIZE = 16 # macro
TMF8829_FRAME_FOOTER_SIZE = 12 # macro

# Frame header - present with every frame
class struct__tmf8829FrameHeader(Structure):
    pass

class struct__tmf8829FrameHeader(Structure):
    """ Frame header - present with every frame """
    def __init__(self, *args):
        self.id: ctypes.c_ubyte
        """ frame identifier unique to specify that this is a result/histogram/spad-scan frame """
        self.layout: ctypes.c_ubyte
        """ result frame: number of peaks, peak-size, noise-strength, crosstalk, subframe number; histogram frame: sub-frame-id, """
        self.payload: ctypes.c_uint16
        """ length of frame in bytes (excluding id, layout and payload field itself) """
        self.fNumber: ctypes.c_uint32
        """ frame number (running index) """
        self.temperature: List[ctypes.c_byte]
        """ temperature in degree celcius as measured by the device """
        self.bdv: ctypes.c_ubyte
        """ BDV value used for measurement """
        self.refPos: List[ctypes.c_uint16]
        """ optical reference peak position in mm notation for 1st and last sub-frame """
        super().__init__(*args)
    _pack_ = 1
    _fields_ = [
    ('id', ctypes.c_ubyte),
    ('layout', ctypes.c_ubyte),
    ('payload', ctypes.c_uint16),
    ('fNumber', ctypes.c_uint32),
    ('temperature', ctypes.c_byte * 3),
    ('bdv', ctypes.c_ubyte),
    ('refPos', ctypes.c_uint16 * 2),
     ]

tmf8829FrameHeader = struct__tmf8829FrameHeader

# Frame footer - present with every frame
class struct__tmf8829FrameFooter(Structure):
    pass

class struct__tmf8829FrameFooter(Structure):
    """ Frame footer - present with every frame """
    def __init__(self, *args):
        self.t0Integration: ctypes.c_uint32
        """ internal timestamp when t0 integration was started """
        self.t1Integration: ctypes.c_uint32
        """ internal timestamp when t1 integration was started """
        self.frameStatus: ctypes.c_ubyte
        """ whether the complete frame is valid or has been invalidated """
        self.reserved: ctypes.c_ubyte
        """ reserved for future use """
        self.eof: ctypes.c_uint16
        """ end of frame marker """
        super().__init__(*args)
    _pack_ = 1
    _fields_ = [
    ('t0Integration', ctypes.c_uint32),
    ('t1Integration', ctypes.c_uint32),
    ('frameStatus', ctypes.c_ubyte),
    ('reserved', ctypes.c_ubyte),
    ('eof', ctypes.c_uint16),
     ]

tmf8829FrameFooter = struct__tmf8829FrameFooter

# 3 bytes used to encode a single peak
class struct__tmf8829Peak(Structure):
    pass

class struct__tmf8829Peak(Structure):
    """ 3 bytes used to encode a single peak """
    def __init__(self, *args):
        self.distance: ctypes.c_uint16
        self.snr: ctypes.c_ubyte
        super().__init__(*args)
    _pack_ = 1
    _fields_ = [
    ('distance', ctypes.c_uint16),
    ('snr', ctypes.c_ubyte),
     ]

tmf8829Peak = struct__tmf8829Peak

# 5 byte used to encode a single peak
class struct__tmf8829PeakSignal(Structure):
    pass

class struct__tmf8829PeakSignal(Structure):
    """ 5 byte used to encode a single peak """
    def __init__(self, *args):
        self.distance: ctypes.c_uint16
        self.snr: ctypes.c_ubyte
        self.signal: ctypes.c_uint16
        """ signal strength """
        super().__init__(*args)
    _pack_ = 1
    _fields_ = [
    ('distance', ctypes.c_uint16),
    ('snr', ctypes.c_ubyte),
    ('signal', ctypes.c_uint16),
     ]

tmf8829PeakSignal = struct__tmf8829PeakSignal
class struct__tmf8829MPResult(Structure):
    pass

class struct__tmf8829MPResult(Structure):
    def __init__(self, *args):
        self.noise: ctypes.c_uint16
        self.xtalk: ctypes.c_uint16
        self.peaks: List[struct__tmf8829PeakSignal]
        super().__init__(*args)
    _pack_ = 1
    _fields_ = [
    ('noise', ctypes.c_uint16),
    ('xtalk', ctypes.c_uint16),
    ('peaks', struct__tmf8829PeakSignal * 4),
     ]

tmf8829MPResult = struct__tmf8829MPResult

# Maximum frame for 8x8, 16x16, 32x32, 48x32 resolution
class struct__tmf8829ResultFrame(Structure):
    pass

class union__tmf8829ResultFrame_0(Union):
    pass

class union__tmf8829ResultFrame_0(Union):
    def __init__(self, *args):
        self.result: List[struct__tmf8829MPResult]
        """ info per MP, placeholder is just one instance """
        self.data: List[ctypes.c_ubyte]
        super().__init__(*args)
    _pack_ = 1
    _fields_ = [
    ('result', struct__tmf8829MPResult * 1),
    ('data', ctypes.c_ubyte * 7684),
     ]

class struct__tmf8829ResultFrame(Structure):
    """ Maximum frame for 8x8, 16x16, 32x32, 48x32 resolution """
    def __init__(self, *args):
        self.header: tmf8829FrameHeader
        self._tmf8829ResultFrame_0: union__tmf8829ResultFrame_0
        self.footer: tmf8829FrameFooter
        super().__init__(*args)
    _pack_ = 1
    _fields_ = [
    ('header', tmf8829FrameHeader),
    ('_tmf8829ResultFrame_0', union__tmf8829ResultFrame_0),
    ('footer', tmf8829FrameFooter),
     ]

tmf8829ResultFrame = struct__tmf8829ResultFrame
class struct__tmf8829RefSpadFrame(Structure):
    pass

class struct__tmf8829RefSpadFrame(Structure):
    def __init__(self, *args):
        self.header: tmf8829FrameHeader
        self.sum: List[List[ctypes.c_uint32]]
        """ nr hits per MP, for both integration cycles """
        self.footer: tmf8829FrameFooter
        super().__init__(*args)
    _pack_ = 1
    _fields_ = [
    ('header', tmf8829FrameHeader),
    ('sum', ctypes.c_uint32 * 4 * 2),
    ('footer', tmf8829FrameFooter),
     ]

tmf8829RefSpadFrame = struct__tmf8829RefSpadFrame
# a single histogram has 64 bins each with up to 24-bit hits
class struct__tmf8829Histogram(Structure):
    pass

class struct__tmf8829Histogram(Structure):
    """ a single histogram has 64 bins each with up to 24-bit hits """
    def __init__(self, *args):
        self.bin: List[ctypes.c_uint32]
        """ in RAM the CPUs operate on the full 32-bit histograms """
        super().__init__(*args)
    _pack_ = 1
    _fields_ = [
    ('bin', ctypes.c_uint32 * 64),
     ]

tmf8829Histogram = struct__tmf8829Histogram
# a single histogram has 256 bins each with up to 24-bit hits
class struct__tmf8829Histogram8x8(Structure):
    pass

class struct__tmf8829Histogram8x8(Structure):
    """ a single histogram has 256 bins each with up to 24-bit hits """
    def __init__(self, *args):
        self.bin: List[ctypes.c_uint32]
        """ in RAM the CPUs operate on the full 32-bit histograms """
        super().__init__(*args)
    _pack_ = 1
    _fields_ = [
    ('bin', ctypes.c_uint32 * 256),
     ]

tmf8829Histogram8x8 = struct__tmf8829Histogram8x8
# a transmitted histogram will compress the bin-content to 24-bits
class struct__tmf8829HistogramCompressed(Structure):
    pass

class struct__tmf8829HistogramCompressed(Structure):
    """ a transmitted histogram will compress the bin-content to 24-bits """
    def __init__(self, *args):
        self.bin: List[ctypes.c_ubyte]
        """ AODMA transfers the histograms to the FIFO and on the fly compresses them from 32-bit to 24-bit, so host reads them like this """
        super().__init__(*args)
    _pack_ = 1
    _fields_ = [
    ('bin', ctypes.c_ubyte * 192),
     ]

tmf8829HistogramCompressed = struct__tmf8829HistogramCompressed
# a transmitted histogram will compress the bin-content to 24-bits
class struct__tmf8829Histogram8x8Compressed(Structure):
    pass

class struct__tmf8829Histogram8x8Compressed(Structure):
    """ a transmitted histogram will compress the bin-content to 24-bits """
    def __init__(self, *args):
        self.bin: List[ctypes.c_ubyte]
        """ AODMA transfers the histograms to the FIFO and on the fly compresses them from 32-bit to 24-bit, so host reads them like this """
        super().__init__(*args)
    _pack_ = 1
    _fields_ = [
    ('bin', ctypes.c_ubyte * 768),
     ]

tmf8829Histogram8x8Compressed = struct__tmf8829Histogram8x8Compressed
# Half histogram frame for 8x8 resolution, histograms are transmitted with 2
# frames
class struct__tmf8829HistogramFrame4x8(Structure):
    pass

class struct__tmf8829HistogramFrame4x8(Structure):
    """ Half histogram frame for 8x8 resolution, histograms are transmitted with 2 frames """
    def __init__(self, *args):
        self.header: tmf8829FrameHeader
        self.refHistograms: List[struct__tmf8829Histogram]
        self.histograms: List[List[struct__tmf8829Histogram8x8]]
        self.footer: tmf8829FrameFooter
        super().__init__(*args)
    _pack_ = 1
    _fields_ = [
    ('header', tmf8829FrameHeader),
    ('refHistograms', struct__tmf8829Histogram * 4),
    ('histograms', struct__tmf8829Histogram8x8 * 4 * 8),
    ('footer', tmf8829FrameFooter),
     ]

tmf8829HistogramFrame4x8 = struct__tmf8829HistogramFrame4x8
class struct__tmf8829HistogramFrame4x8Compressed(Structure):
    pass

class struct__tmf8829HistogramFrame4x8Compressed(Structure):
    def __init__(self, *args):
        self.header: tmf8829FrameHeader
        self.refHistograms: List[struct__tmf8829HistogramCompressed]
        self.histograms: List[List[struct__tmf8829Histogram8x8Compressed]]
        self.footer: tmf8829FrameFooter
        super().__init__(*args)
    _pack_ = 1
    _fields_ = [
    ('header', tmf8829FrameHeader),
    ('refHistograms', struct__tmf8829HistogramCompressed * 4),
    ('histograms', struct__tmf8829Histogram8x8Compressed * 4 * 8),
    ('footer', tmf8829FrameFooter),
     ]

tmf8829HistogramFrame4x8Compressed = struct__tmf8829HistogramFrame4x8Compressed
# Half histogram frame for 16x16 resolution, histograms are transmitted with 2
# frames
class struct__tmf8829HistogramFrame8x16(Structure):
    pass

class struct__tmf8829HistogramFrame8x16(Structure):
    """ Half histogram frame for 16x16 resolution, histograms are transmitted with 2 frames """
    def __init__(self, *args):
        self.header: tmf8829FrameHeader
        self.refHistograms: List[struct__tmf8829Histogram]
        self.histograms: List[List[struct__tmf8829Histogram]]
        self.footer: tmf8829FrameFooter
        super().__init__(*args)
    _pack_ = 1
    _fields_ = [
    ('header', tmf8829FrameHeader),
    ('refHistograms', struct__tmf8829Histogram * 4),
    ('histograms', struct__tmf8829Histogram * 8 * 16),
    ('footer', tmf8829FrameFooter),
     ]

tmf8829HistogramFrame8x16 = struct__tmf8829HistogramFrame8x16
class struct__tmf8829HistogramFrame8x16Compressed(Structure):
    pass

class struct__tmf8829HistogramFrame8x16Compressed(Structure):
    def __init__(self, *args):
        self.header: tmf8829FrameHeader
        self.refHistograms: List[struct__tmf8829HistogramCompressed]
        self.histograms: List[List[struct__tmf8829HistogramCompressed]]
        self.footer: tmf8829FrameFooter
        super().__init__(*args)
    _pack_ = 1
    _fields_ = [
    ('header', tmf8829FrameHeader),
    ('refHistograms', struct__tmf8829HistogramCompressed * 4),
    ('histograms', struct__tmf8829HistogramCompressed * 8 * 16),
    ('footer', tmf8829FrameFooter),
     ]

tmf8829HistogramFrame8x16Compressed = struct__tmf8829HistogramFrame8x16Compressed
__all__ = \
    ['TMF8829_APPLICATION_CAPABILITIES',
    'TMF8829_APPLICATION_ID',
    'TMF8829_APPLICATION_MAJOR', 'TMF8829_APPLICATION_MINOR',
    'TMF8829_FID_HISTOGRAMS',
    'TMF8829_FID_MASK', 'TMF8829_FID_REF_SPAD_SCAN',
    'TMF8829_FID_RESULTS',
    'TMF8829_FPM_MASK',
    'TMF8829_FRAME_ABORTED', 'TMF8829_FRAME_EOF',
    'TMF8829_FRAME_FOOTER_SIZE', 'TMF8829_FRAME_HEADER_OFFSET',
    'TMF8829_FRAME_HEADER_SIZE', 'TMF8829_FRAME_VALID',
    'TMF8829_FRAME_WARNING_HV_CP_OVERLOAD',
    'TMF8829_FRAME_WARNING_VCDRV_BURST_EXCEEDED',
    'TMF8829_FRAME_WARNING_VCDRV_OVERLOAD',
    'TMF8829_INT_HISTOGRAMS',
    'TMF8829_INT_RESULTS',
    'TMF8829_MAX_PEAKS_PER_MP',
    'struct__tmf8829FrameFooter', 'struct__tmf8829FrameHeader',
    'struct__tmf8829Histogram', 'struct__tmf8829Histogram8x8',
    'struct__tmf8829Histogram8x8Compressed',
    'struct__tmf8829HistogramCompressed',
    'struct__tmf8829HistogramFrame4x8',
    'struct__tmf8829HistogramFrame4x8Compressed',
    'struct__tmf8829HistogramFrame8x16',
    'struct__tmf8829HistogramFrame8x16Compressed',
    'struct__tmf8829MPResult', 'struct__tmf8829Peak',
    'struct__tmf8829PeakSignal', 'struct__tmf8829RefSpadFrame',
    'struct__tmf8829ResultFrame', 'tmf8829FrameFooter',
    'tmf8829FrameHeader', 'tmf8829Histogram', 'tmf8829Histogram8x8',
    'tmf8829Histogram8x8Compressed', 'tmf8829HistogramCompressed',
    'tmf8829HistogramFrame4x8', 'tmf8829HistogramFrame4x8Compressed',
    'tmf8829HistogramFrame8x16',
    'tmf8829HistogramFrame8x16Compressed', 'tmf8829MPResult',
    'tmf8829Peak', 'tmf8829PeakSignal', 'tmf8829RefSpadFrame',
    'tmf8829ResultFrame', 'union__tmf8829ResultFrame_0']
