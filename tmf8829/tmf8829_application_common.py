# *****************************************************************************
# * Copyright by ams OSRAM AG                                                 *
# * All rights are reserved.                                                  *
# *                                                                           *
# *FOR FULL LICENSE TEXT SEE LICENSES-MIT.TXT                                 *
# *****************************************************************************
"""
The TMF8829 common application class.
Generel helper functions that could be used for data processing or
for applications with device connection.
"""

import __init__

import ctypes

from tmf8829_application_defines import *
from tmf8829_application_registers import Tmf8829_application_registers as Tmf8829AppRegs
from tmf8829_config_page import Tmf8829_config_page as Tmf8829ConfigRegs
from tmf8829_host_regs import Tmf8829_host_regs as Tmf8829HostRegs

from aos_com.register_io import ctypes2Dict

class Tmf8829AppCommon():
    """The TMF8829 common application class with common functions.
    """
    FP_MODE_8x8A   = Tmf8829ConfigRegs.TMF8829_CFG_FP_MODE._fp_mode._FP_8x8A
    FP_MODE_8x8B   = Tmf8829ConfigRegs.TMF8829_CFG_FP_MODE._fp_mode._FP_8x8B
    FP_MODE_16x16  = Tmf8829ConfigRegs.TMF8829_CFG_FP_MODE._fp_mode._FP_16x16
    FP_MODE_32x32  = Tmf8829ConfigRegs.TMF8829_CFG_FP_MODE._fp_mode._FP_32x32
    FP_MODE_32x32s = Tmf8829ConfigRegs.TMF8829_CFG_FP_MODE._fp_mode._FP_32x32s
    FP_MODE_48x32  = Tmf8829ConfigRegs.TMF8829_CFG_FP_MODE._fp_mode._FP_48x32

    MP_FOV_ROWS       = 16 # number of pixel in FOV in y-direction
    MP_FOV_COLUMNS    = 16 # number of pixel in FOV in x-direction

    REF_PIXEL_ROWS    = 2
    REF_PIXEL_COLUMNS = 2
    REF_PIXEL         = REF_PIXEL_COLUMNS * REF_PIXEL_ROWS
    
    PRE_HEADER_SIZE   = 5
    
    RESULT_FRAME_SUBIDX_SHIFT = Tmf8829ConfigRegs.TMF8829_CFG_RESULT_FORMAT._sub_result.shift
    RESULT_FRAME_SUBIDX_MASK =  Tmf8829ConfigRegs.TMF8829_CFG_RESULT_FORMAT._sub_result.mask    # sub-result frame bit
    
    VERSION = 1.10
    """Version log
    - 1.0 ... splitted up tmf8829_application to tmf8829_application_common and tmf8829_application

    """

    @staticmethod
    def binsPerHistograms(fpMode):
        """Function returns the number of bins per histogram. (256 or 64)
        Args:
            fpMode (int): is one of the following: FP_MODE_8x8A, FP_MODE_8x8B,
            FP_MODE_16x16, FP_MODE_32x32,FP_MODE_32x32s or FP_MODE_48x32
        Return:
            int: number of bins
        """
        if fpMode > Tmf8829AppCommon.FP_MODE_8x8B:
            return 64
        else:
            return 256

    @staticmethod
    def histogramsPerFrame(fpMode):
        """Function returns the number of histograms per frame. (4x8 or 8x16)
        Args:
            fpMode (int): is one of the following: FP_MODE_8x8A, FP_MODE_8x8B,
            FP_MODE_16x16, FP_MODE_32x32 or FP_MODE_32x32s
        Return:
            int: number of histograms per frame
        """
        if fpMode > Tmf8829AppCommon.FP_MODE_8x8B:
            return 8*16
        else:
            return 4*8

    @staticmethod
    def pixelRows(fpMode) -> int:
        """Function returns the number of pixel rows in the focal plan.
        Args:
            fpMode (int): is one of the following: FP_MODE_8x8A, FP_MODE_8x8B,
            FP_MODE_16x16, FP_MODE_32x32 or FP_MODE_32x32s
        Return:
            int: number of pixel rows
        """
        if fpMode > Tmf8829AppCommon.FP_MODE_8x8B:
            if fpMode > Tmf8829AppCommon.FP_MODE_16x16:
                if fpMode > Tmf8829AppCommon.FP_MODE_32x32s:
                    return 32
                else:
                    return 32
            else:
                return 16
        else:
            return 8

    @staticmethod
    def pixelColumns(fpMode) -> int:
        """Function returns the number of pixel columns in the focal plan.
        Args:
            fpMode (int): is one of the following: FP_MODE_8x8A, FP_MODE_8x8B,
            FP_MODE_16x16, FP_MODE_32x32 or FP_MODE_32x32s
        Return:
            int: number of pixel columns
        """
        if fpMode > Tmf8829AppCommon.FP_MODE_8x8B:
            if fpMode > Tmf8829AppCommon.FP_MODE_16x16:
                if fpMode > Tmf8829AppCommon.FP_MODE_32x32s:
                    return 48
                else:
                    return 32
            else:
                return 16
        else:
            return 8

    @staticmethod
    def numberPixel(fpMode) -> int:
        """Number of pixel in focal plan (8x8 or 16x16 or 32x32 or 48x32)
        Args:
            fpMode (int): is one of the following: FP_MODE_8x8A, FP_MODE_8x8B,
            FP_MODE_16x16, FP_MODE_32x32 or FP_MODE_32x32s
        Return:
            int: number of pixel  
        """
        return Tmf8829AppCommon.pixelRows(fpMode) * Tmf8829AppCommon.pixelColumns(fpMode)

    @staticmethod
    def resultsPerFrame(fpMode):
        """Function returns results per frame (8x8 or 16x16 or 32x16)
        Args:
            fpMode (int): is one of the following: FP_MODE_8x8A, FP_MODE_8x8B,
            FP_MODE_16x16, FP_MODE_32x32 or FP_MODE_32x32s
        Return:
            int: results per frame
        """
        if fpMode > Tmf8829AppCommon.FP_MODE_16x16:
            if fpMode > Tmf8829AppCommon.FP_MODE_32x32s:
                return 48*16   # 2 frames are needed
            else:
                return 32*16    # 2 frames are needed
        elif fpMode == Tmf8829AppCommon.FP_MODE_16x16:
            return 16*16
        else:
            return 8*8

    @staticmethod
    def pixelResultSize(resultFormat):
        """Function returns the number of bytes that a single MP (pixel) returns
        Args:
            resultFormat (int): format byte that defines the number of peaks per MP and also the size of the peak description, etc.
        Return:
            int: bytes per pixel
        """
        _numPeak = resultFormat & Tmf8829ConfigRegs.TMF8829_CFG_RESULT_FORMAT._nr_peaks.mask
        _useSignal = 1 if (resultFormat & Tmf8829ConfigRegs.TMF8829_CFG_RESULT_FORMAT._signal_strength.mask)==Tmf8829ConfigRegs.TMF8829_CFG_RESULT_FORMAT._signal_strength.mask else 0
        _useNoise = 1 if (resultFormat & Tmf8829ConfigRegs.TMF8829_CFG_RESULT_FORMAT._noise_strength.mask)==Tmf8829ConfigRegs.TMF8829_CFG_RESULT_FORMAT._noise_strength.mask else 0
        _useXtalk = 1 if (resultFormat & Tmf8829ConfigRegs.TMF8829_CFG_RESULT_FORMAT._xtalk.mask)==Tmf8829ConfigRegs.TMF8829_CFG_RESULT_FORMAT._xtalk.mask else 0
        _size = ( _numPeak * ( 3 + 2 * _useSignal) ) + ( 2 * _useNoise ) + ( 2 * _useXtalk )
        return _size

    @staticmethod
    def resultFrameDataSize(fpMode,resultFormat):
        """Function returns the number of bytes in the result of a frame. Excluding frame header and frame footer.
        Args:
            fpMode (int): is one of the following: FP_MODE_8x8A, FP_MODE_8x8B,
            FP_MODE_16x16, FP_MODE_32x32, FP_MODE_32x32s or FP_MODE_48x32
            resultFormat: format byte that defines the number of peaks per MP and also the size of the peak description, etc.
        Return:
            int: bytes of frame
        """
        _size = Tmf8829AppCommon.pixelResultSize(resultFormat)
        _size = _size * Tmf8829AppCommon.resultsPerFrame( fpMode )
        return _size

    @staticmethod
    def histogramFrameDataSize(fpMode):
        """Function returns the number of bytes in a histogram frame. excluding frame header and frame footer
        Args:
            fpMode (int): is one of the following: FP_MODE_8x8A, FP_MODE_8x8B,
            FP_MODE_16x16, FP_MODE_32x32, FP_MODE_32x32s or FP_MODE_48x32
        Return:
            int: bytes of histogram frame
        """
        _bytes_per_bin = 3
        _bins = 64                  # reference pixel always have only 64 bins
        _size = 64 * _bytes_per_bin * Tmf8829AppCommon.REF_PIXEL 
        _bins = Tmf8829AppCommon.binsPerHistograms(fpMode)                # MP can have 64 or 256 bins 
        _size += _bins * _bytes_per_bin * Tmf8829AppCommon.histogramsPerFrame(fpMode) 
        return _size

    @staticmethod
    def numberOfHistogramFramesPerMeasurement(fpMode, dualMode = 0 ):
        """ Returns the number of histograms frames for one Measurement

        Args:
            fpMode (int): is one of the following: FP_MODE_8x8A, FP_MODE_8x8B,
                          FP_MODE_16x16, FP_MODE_32x32, FP_MODE_32x32s or FP_MODE_48x32
            dualMode (int, optional): dual mode is set. Defaults to 0.

        Returns:
            int: number of histogram frames for one measurement
        """
        
        _histograms = 2
        if fpMode > Tmf8829AppCommon.FP_MODE_16x16:
            _histograms = 8        # 32x32 has 8
        if fpMode == Tmf8829AppCommon.FP_MODE_48x32:
            _histograms = 12        # 48x32 has 12
        
        if dualMode == 1:
            _histograms = _histograms*2

        return _histograms

    @staticmethod
    def numberOfFrameReadsPerMeasurement(fpMode,rawHistograms, dualMode = 0 ):
        """Number of histogram + frames that complete one measurement, and takes into account if raw histogram frames are produced or not.
           Ignores reference frames as they come together with result frames (8x8, 16x16, 32x32, 48x32)
        Args:
            fpMode (int): is one of the following: FP_MODE_8x8A, FP_MODE_8x8B,
            FP_MODE_16x16, FP_MODE_32x32, FP_MODE_32x32s or FP_MODE_48x32
            rawHistograms (int): if set then raw histograms are provided
            dualMode (int): dual mode is enabled
        Return:
            int: number of calls to readFrame function
        """
        _frames = 1
        _histograms = 2
        if fpMode > Tmf8829AppCommon.FP_MODE_16x16:
            _histograms = 8        # 32x32 has 8
            _frames += 1           # two results
        if fpMode == Tmf8829AppCommon.FP_MODE_48x32:
            _histograms = 12        # 48x32 has 12
        if not rawHistograms:
            _histograms = 0

        if dualMode == 1:
            _histograms = _histograms*2

        return _histograms + _frames
    
    @staticmethod
    def getHistograms(data, fpMode):
        """Function that returns the reference and pixel histograms from a histogram frame
        Args:
            data (bytearray): page to be written
        Returns:
            tuple( List[List[tmf8829Histogram]] | List[List[tmf8829Histogram|tmf8829Histogram8x8]):
            Reference Histograms [r][b], Histograms [y][x][b]
        """
        _header_size = ctypes.sizeof(struct__tmf8829FrameHeader)
        _bins = Tmf8829AppCommon.binsPerHistograms( fpMode )
        xx = 8
        yy = 16
        if fpMode < Tmf8829AppCommon.FP_MODE_16x16:
            xx = 4
            yy = 8

        _ref_hist = [tmf8829Histogram() for _ in range(4)]
        if fpMode < Tmf8829AppCommon.FP_MODE_16x16:
            _hist = [[tmf8829Histogram8x8() for _ in range(xx)] for _ in range(yy)]
        else:
            _hist = [[tmf8829Histogram() for _ in range(xx)] for _ in range(yy)]

        _idx = Tmf8829AppCommon.PRE_HEADER_SIZE+_header_size
        for r in range(4):
            for b in range(64):
                _ref_hist[r].bin[b] = int.from_bytes( data[_idx:_idx+3], byteorder = 'little', signed=False )
                _idx += 3
        for y in range(yy):
            for x in range(xx):
                for b in range(_bins):
                    _hist[y][x].bin[b] = int.from_bytes( data[_idx:_idx+3], byteorder = 'little', signed=False )
                    _idx += 3
        return _ref_hist, _hist

    @staticmethod
    def getPixelResult(data, resultFormat):
        """Return the tmf8829MPResult structure with noise, xtalk and peaks information,
           where the peaks are a list of tmf8829PeakSignal structures with distance, snr, signal information

        Args:
            data : result data
            resultFormat: format byte that defines the number of peaks per MP and also the size of the peak description, etc.
        Returns:
            tmf8829MPResult : tmf8829MPResult structure
        """
        _numPeak = resultFormat & Tmf8829ConfigRegs.TMF8829_CFG_RESULT_FORMAT._nr_peaks.mask
        _useSignal = 1 if (resultFormat & Tmf8829ConfigRegs.TMF8829_CFG_RESULT_FORMAT._signal_strength.mask)==Tmf8829ConfigRegs.TMF8829_CFG_RESULT_FORMAT._signal_strength.mask else 0
        _useNoise = 1 if (resultFormat & Tmf8829ConfigRegs.TMF8829_CFG_RESULT_FORMAT._noise_strength.mask)==Tmf8829ConfigRegs.TMF8829_CFG_RESULT_FORMAT._noise_strength.mask else 0
        _useXtalk = 1 if (resultFormat & Tmf8829ConfigRegs.TMF8829_CFG_RESULT_FORMAT._xtalk.mask)==Tmf8829ConfigRegs.TMF8829_CFG_RESULT_FORMAT._xtalk.mask else 0

        _psNone = ctypes2Dict(tmf8829PeakSignal())
        _psNone["distance"] = None
        _psNone["snr"] = None
        _psNone["signal"] = None
        _mpResult = ctypes2Dict(tmf8829MPResult())
        _mpResult["noise"] = None
        _mpResult["xtalk"] = None
        _mpResult["peaks"] = [_psNone,_psNone,_psNone,_psNone]

        _idx =0
        if _useNoise:
            _mpResult["noise"] = data[_idx] + data[_idx+1]*256
            _idx +=2
        if _useXtalk:
            _mpResult["xtalk"] = data[_idx] + data[_idx+1]*256
            _idx += 2
        for p in range(_numPeak):
            ps = ctypes2Dict(tmf8829PeakSignal())
            ps["distance"] = data[_idx] + data[_idx+1]*256
            ps["snr"] = data[_idx+2]
            _idx += 3
            if _useSignal:
                ps["signal"] = data[_idx] + data[_idx+1]*256
                _idx +=2
            else:
                ps["signal"] = None

            _mpResult["peaks"][p]= ps

        return _mpResult

    @staticmethod
    def getPixelResultsFromFrame(data, fpMode, resultFormat):
        """Function returns the results of tmf8829MPResult structures in tuples[y|x]
        Args:
            data (bytearray): a result frame (including the header but not the 5 registers 0xFA..0xFE with SYS-TICK)
            fpMode (int): is one of the following: FP_MODE_8x8A, FP_MODE_8x8B,
            FP_MODE_16x16, FP_MODE_32x32, FP_MODE_32x32s or FP_MODE_48x32
            resultFormat (int): format byte that defines the number of peaks per MP and also the size of the peak description, etc.
        Returns:
            tuples[y|x] of tmf8829MPResult structures
        """
        _header_size = ctypes.sizeof(struct__tmf8829FrameHeader)
        xx = 16
        yy = 16
        pixelDataSize = Tmf8829AppCommon.pixelResultSize(resultFormat)
        if fpMode < Tmf8829AppCommon.FP_MODE_16x16:
            xx = 8
            yy = 8
        if fpMode > Tmf8829AppCommon.FP_MODE_16x16:
            if fpMode > Tmf8829AppCommon.FP_MODE_32x32s:
                xx = 48
                yy = 16 # half in y
            else:
                xx = 32
                yy = 16 # half in y
        results = [ [ tmf8829MPResult() for _ in range(xx)] for __ in range(yy)]
        for y in range(yy):
            for x in range(xx):
                _idx = Tmf8829AppCommon.PRE_HEADER_SIZE+_header_size+(y*xx+x)*pixelDataSize
                results[y][x] = Tmf8829AppCommon.getPixelResult(data[_idx:_idx+pixelDataSize], resultFormat)

        return results

    @staticmethod
    def getFramesFromMeasurementResult(result_data:bytes):
        """The result set of a measurement is split in single frames and returned.
        Arg: 
            result_data (bytes): bytes of mesurement result.
        Returns:
            tuple(list[bytearray],list[bytearray],list[bytearray]): returns the list of result frames,
                list of histogram frames and list of reference frames.
        """
        framebytes = bytearray(result_data)
        histo_frames = []
        result_frames = []
        ref_frames =[]                              # ref-frames are special, they are not read from fifo but from plain registers
        while len(framebytes) > 0:
            if ( framebytes[Tmf8829AppCommon.PRE_HEADER_SIZE] & TMF8829_FID_MASK )== TMF8829_FID_REF_SPAD_SCAN:
                _size = Tmf8829AppCommon.PRE_HEADER_SIZE+ctypes.sizeof(struct__tmf8829RefSpadFrame)
                frame = framebytes[0:_size]         # frame is preheader + frame-itself
                framebytes = framebytes[_size:]     # remove frame preheader + frame-itself
                ref_frames.append(frame)
            else:
                _size =Tmf8829AppCommon.PRE_HEADER_SIZE+ctypes.sizeof(struct__tmf8829FrameHeader)
                _header = tmf8829FrameHeader.from_buffer_copy( framebytes[Tmf8829AppCommon.PRE_HEADER_SIZE:_size])
                _size = Tmf8829AppCommon.PRE_HEADER_SIZE + 4 + _header.payload    # 4 for the HEADER 4-bytes that are not part of the payload
                frame = framebytes[0:_size]         # frame is preheader + frame-itself
                if ( _header.id & TMF8829_FID_MASK ) == TMF8829_FID_RESULTS:
                    result_frames.append(frame)
                elif ( _header.id & TMF8829_FID_MASK ) == TMF8829_FID_HISTOGRAMS:
                    histo_frames.append(frame)
                framebytes = framebytes[_size:]     # remove frame preheader + frame-itself
        return result_frames, histo_frames, ref_frames

    @staticmethod
    def getFullPixelResult(frames, toMM = False, deleteNone = True, pointCloud = False, distanceToXYZ =False):
        """Function that takes the result frames, and returns a list with tmf8829MPResult structures for every pixel.
        Args:
            frames: list[bytearray] the result frames in the right order as received by the device.
            toMM: Changes the distance results from 0.25mm to mm. Note do not use this option if the results are in bins
            deleteNone: Remove None items from MP Results.
            pointCloud: do point cloud correction, only done if distanceToXYZ = False
            distanceToXYZ: reports distance the xyz values, if this option is used, the distance will not be point cloud corrected.
        Returns:
            List[row][col] tmf8829MPResult structures
        """
        _header = tmf8829FrameHeader.from_buffer_copy( frames[0][Tmf8829AppCommon.PRE_HEADER_SIZE:Tmf8829AppCommon.PRE_HEADER_SIZE+ctypes.sizeof(struct__tmf8829FrameHeader)])
        fpMode = _header.id & TMF8829_FPM_MASK

        pixelResults = Tmf8829AppCommon.getPixelResultsFromFrame(list(frames[0]),fpMode,resultFormat=_header.layout)
        
        if fpMode > Tmf8829AppCommon.FP_MODE_16x16 and len(frames) == 2:
            resultsMpDownRow = Tmf8829AppCommon.getPixelResultsFromFrame(list(frames[1]),fpMode,_header.layout)
            for row in range(len(resultsMpDownRow)):
                pixelResults.insert(row*2+1, resultsMpDownRow[row]) 
        
        if toMM:
            pixelResults = Tmf8829AppCommon.pixelResultsToMM(pixelResults)

        if deleteNone:
            pixelResults = Tmf8829AppCommon.pixelResultsDeleteNoneParam(pixelResults)

        if (pointCloud == True) or (distanceToXYZ  == True):
            Tmf8829AppCommon.pixelResults3dPointcloudCorr(pixelResults, fpMode, reportXYZ= distanceToXYZ)

        return pixelResults

    @staticmethod
    def pixelResultsToMM(pixelResults):
        """Function changes the distance results from 0.25mm to mm.
        Args:
            list[list[tmf8829MPResult]]: tmf8829MPResult structures; List[row][col]
        Returns:
            list[list[tmf8829MPResult]]: tmf8829MPResult structures; List[row][col]
        """
        for rowsMp in pixelResults:
            for mp in rowsMp:
                for peaks in mp['peaks']:
                    if peaks['distance'] != None:
                        distance = peaks['distance']
                        distance1mm = distance / 4 
                        peaks['distance']= distance1mm

        return pixelResults
    
    @staticmethod
    def pixelResults3dPointcloudCorr(pixelResults, fp_mode, reportXYZ=False):
        """Function changes the distance results with the 3d Point cloud correction.
            fpMode (int): is one of the following: FP_MODE_8x8A, FP_MODE_8x8B,
            FP_MODE_16x16, FP_MODE_32x32, FP_MODE_32x32s or FP_MODE_48x32
        Args:
            list[list[tmf8829MPResult]]: tmf8829MPResult structures; List[row][col]
            fpMode (int): is one of the following: FP_MODE_8x8A, FP_MODE_8x8B,
                FP_MODE_16x16, FP_MODE_32x32, FP_MODE_32x32s or FP_MODE_48x32
            reportXYZ: instead of distance xyz values are reported
        Returns:
            list[list[tmf8829MPResult]]: tmf8829MPResult structures; List[row][col]
            or 
            list[list[]]:tmf8829MPResult structures, x y z - values instead of distances; List[row][col]         
        """

        for y, pixelRow in enumerate( pixelResults ):
            for x, pixel in enumerate( pixelRow ):
                 # get correction factor
                if reportXYZ:
                    zCorrSimple, x_dist, y_dist = Tmf8829AppCommon.zCorrection(pixel_x=x,pixel_y=y,fp_mode=fp_mode, getxy=reportXYZ)
                else: 
                    zCorrSimple = Tmf8829AppCommon.zCorrection(pixel_x=x,pixel_y=y,fp_mode=fp_mode)
                for peak in pixel['peaks']:
                    if peak['distance'] != None:
                        if reportXYZ:
                            distanceCorr = peak['distance'] / zCorrSimple
                            # peak.pop("distance") do not remove distance 
                            peak['x']= round(distanceCorr*x_dist)
                            peak['y']= round(distanceCorr*y_dist)
                            peak['z']= round(distanceCorr)
                        else:
                            distanceCorr = peak['distance'] / zCorrSimple
                            peak['distance']= round(distanceCorr)
        
        return pixelResults

    @staticmethod
    def getAllHistogramResults(frames):
        """Function that takes the histogram frames, and returns mp histograms and reference histograms.
        Args:
            frames:list[bytearray] the histogram frames
        Returns:
            tuple( List[List[tmf8829Histogram]] | List[List[tmf8829Histogram|tmf8829Histogram8x8]):
            Reference Histograms [r][b], Histograms [y][x][b]
        """

        _header_size = ctypes.sizeof(struct__tmf8829FrameHeader)
        _header = tmf8829FrameHeader.from_buffer_copy(bytearray(frames[0][Tmf8829AppCommon.PRE_HEADER_SIZE:Tmf8829AppCommon.PRE_HEADER_SIZE+_header_size]))
        fpMode = _header.id & TMF8829_FPM_MASK

        fov_rows = Tmf8829AppCommon.MP_FOV_ROWS
        fov_columns = Tmf8829AppCommon.MP_FOV_COLUMNS
        if fpMode < Tmf8829AppCommon.FP_MODE_16x16:
            fov_rows = int(Tmf8829AppCommon.MP_FOV_ROWS/2)
            fov_columns = int(Tmf8829AppCommon.MP_FOV_COLUMNS/2)

        pixelColumns = Tmf8829AppCommon.pixelColumns(fpMode)
        pixelRows = Tmf8829AppCommon.pixelRows(fpMode)
        pixelColumnsPerMp = int(pixelColumns / fov_columns)
        pixelRowsPerMp = int(pixelRows / fov_rows)
        
        sumRefHistograms = []
        sumMpHistograms  = [[[] * Tmf8829AppCommon.binsPerHistograms(fpMode) for _ in range(pixelColumns)] for _ in range(pixelRows)]

        for frame in frames:
            _header = tmf8829FrameHeader.from_buffer_copy(bytearray(frame[Tmf8829AppCommon.PRE_HEADER_SIZE:Tmf8829AppCommon.PRE_HEADER_SIZE+_header_size]))
            #print( "Header FID={} Layout/Sub={} Payload={} FrameNumber={} bdv={} ".format(_header.id,_header.layout,_header.payload,_header.fNumber,_header.bdv),end="")
            ref_histo, histogram = Tmf8829AppCommon.getHistograms(frame, fpMode)
            
            leftFovOffset = 0
            pixelRowOffset = 0
            pixelColumnOffset = 0
            if _header.layout %2 != 0: # for odd layouts
                leftFovOffset = int(pixelColumns/2)
            
            if fpMode <= Tmf8829AppCommon.FP_MODE_32x32s:
                if _header.layout in [2,3,6,7]:
                    pixelColumnOffset = 1
                if _header.layout > 3:
                    pixelRowOffset = 1
            elif fpMode == Tmf8829AppCommon.FP_MODE_48x32: 
                if _header.layout in [2,3,8,9]:
                    pixelColumnOffset = 1
                if _header.layout in [4,5,10,11]:
                    pixelColumnOffset = 2
                if _header.layout > 5:
                    pixelRowOffset = 1

            for i in range(0, fov_rows):
                for j in range(0, int(fov_columns/2)):
                    sumMpHistograms[i*pixelRowsPerMp+pixelRowOffset][j*pixelColumnsPerMp+leftFovOffset+ pixelColumnOffset] = histogram[i][j]

            sumRefHistograms += ref_histo # append the reference Histograms

        return sumRefHistograms, sumMpHistograms

    @staticmethod
    def getAllHistogramResultsDualMode(frames):
        """Function that takes the histogram frames, and returns mp histograms and reference histograms.
        Args:
            frames:list[bytearray] the histogram frames
        Returns:
            tuple( List[List[tmf8829Histogram]] | List[List[tmf8829Histogram|tmf8829Histogram8x8]
                 | List[List[tmf8829Histogram]] | List[List[tmf8829Histogram|tmf8829Histogram8x8]):
            Reference Histograms High Accuracy [r][b], Histograms High Accuracy [y][x][b],
            Reference Histograms [r][b], Histograms [y][x][b]
        """
        fpMode = frames[0][5]&TMF8829_FPM_MASK
        numHistoMode = Tmf8829AppCommon.numberOfHistogramFramesPerMeasurement(fpMode)
        if fpMode <= Tmf8829AppCommon.FP_MODE_16x16:
            haHistoFr = frames[0:numHistoMode]
            lgHistoFr = frames[numHistoMode:]
        else:
            numHistoModeSide = int( numHistoMode / 2 )
            haHistoFr = frames[(numHistoModeSide*0):(numHistoModeSide*1)]
            lgHistoFr = frames[(numHistoModeSide*1):(numHistoModeSide*2)]
            haHistoFr += frames[(numHistoModeSide*2):(numHistoModeSide*3)]
            lgHistoFr += frames[(numHistoModeSide*3):(numHistoModeSide*4)]


        refhistogramResults, histogramResults = Tmf8829AppCommon.getAllHistogramResults(haHistoFr)
        refhistogramResultsLR, histogramResultsLR = Tmf8829AppCommon.getAllHistogramResults(lgHistoFr)

        return refhistogramResults, histogramResults, refhistogramResultsLR, histogramResultsLR

    @staticmethod
    def delete_none_values(_dict):
        """Delete None values recursively and the empty peaks
        Args:
            _dict (dict): Dictonary with None attributes.

        Returns:
            dict: Dictonary without None attributes.
        """    
        for key, value in list(_dict.items()):
            if isinstance(value, dict):
                Tmf8829AppCommon.delete_none_values(value)
            elif value is None:
                del _dict[key]
            elif isinstance(value, list):
                for v_i in value:
                    if isinstance(v_i, dict):
                        Tmf8829AppCommon.delete_none_values(v_i)
                for v_i in value[:]:
                    if v_i == {}:
                        value.remove(v_i)
        return _dict

    @staticmethod
    def pixelResultsDeleteNoneParam(pixelResults):
        """Function remove None items from MP Results.
        Args:
            list[list[tmf8829MPResult]]: tmf8829MPResult structures; List[row][col]
        Returns:
            list[list[tmf8829MPResult]]: tmf8829MPResult structures; List[row][col]
        """
        for rowsMp in pixelResults:
            for mp in rowsMp:
                Tmf8829AppCommon.delete_none_values(mp)
        
        return pixelResults
    
    @staticmethod
    def zCorrection(pixel_x, pixel_y, fp_mode, getxy = False ):
        """Calculates the correction factor for the (virtual) pixel based on the 
        number of spad-per-pixel, and the x/y coordinates of the pixel. Note that this are virtual
        pixels. 
        E.g. in 8x8 mode a virtual pixel has the indices 0..7 and spad_per_pixel_x=6, spad_per_pixel_y=4
        E.g. in 16x16 mode a virtual pixel has the indices 0..15 and spad_per_pixel_x=3, spad_per_pixel_y=2
        E.g. in 32x32 mode a virtual pixel has the indices 0..31 and spad_per_pixel_x=1.5, spad_per_pixel_y=1
        E.g. in 48x32 mode a virtual pixel has the indices 0..47 and spad_per_pixel_x=1, spad_per_pixel_y=1
        Args:
            pixel_x: x-index of the virtual pixel (0..7, 0..15, 0..31, 0..47)
            pixel_y: y-index of the virtual pixel (0..7, 0..15, 0..31)
            fp_mode: 0/1 = 8x8, 2 = 16x16, 3/4 = 32x32, else 48x32
            getxy: reports x and y
        Returns:
            Return a correction factor for x/y position for a single pixel, if getxy = True reports x and y
        """
        import math
        if fp_mode == 0 or fp_mode == 1:
            X = 8
            Y = 8
        elif fp_mode == 2:
            X = 16
            Y = 16
        elif fp_mode == 3 or fp_mode == 4:
            X = 32
            Y = 32
        else:
            X = 48
            Y = 32
        spanX = X * 3.0 / 4.0    
        spanY = Y

        x = ( pixel_x - (X/2) + 0.5 ) / spanX
        y = ( pixel_y - (Y/2) + 0.5 ) / spanY

        if getxy:
            return math.sqrt( 1 + x*x + y*y ), x, y

        return math.sqrt( 1 + x*x + y*y )
