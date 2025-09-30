# *****************************************************************************
# * Copyright by ams OSRAM AG                                                 *
# * All rights are reserved.                                                  *
# *                                                                           *
# *FOR FULL LICENSE TEXT SEE LICENSES-MIT.TXT                                 *
# *****************************************************************************

""" Provides Logger functionality and service for the TMF8829 application and TmF8829 zeromq server/client
"""

import __init__
import time
import os
import json
import gzip
import copy
import sys

from tmf8829_application_common import *

class TMF8829Logger:

    _output_file =""
    _json_dump = {}
    _serial_number = 0

    def __init__(self) -> None:
        self._output_file =""
        self._json_dump = {}
    
    @staticmethod
    def readCfgFile( filePathName:str, in_config:dict = None ) -> dict:
        """ Read the configuration of a json file.
        The configuration in the file is in a python dictionary format

        Args:
            filePathName (str): The path with file name to the config file
            in_config (dict): The read configuration data will be added to this configuration.
        Returns:
            dict: the configuration 
        """
        _basename = os.path.basename(filePathName)

        if _basename.startswith( "cfg" ) and _basename.endswith(".json"): # Config file
            with open(filePathName, "r") as f:
                patch = json.load(f)
                if in_config:
                    cfg = copy.deepcopy(in_config)
                    TMF8829Logger.patch_dict(cfg, patch)
                    return cfg
                else:
                    return patch

    def createLogFile(self, prefix:str, serial_number:list, fw_version:list) -> str:
        """Create a filename with a Prefix, UID and FW version.
           This file will appended all log and dump data.
        Args:
            prefix (str): output file name prefix
            serial_number (list): device serial number
            fw_version (list): firmware version numbers

        Returns:
            str: output log filename
        """
        # Assemble the filename in the following format : prefix_UIDserial_number_FWfw_version_YYYY_MM_DD_HH_MM_SS.json
        time_now = time.localtime()
        time_sep = "-"
        self._output_file = "{}_UID{}-{}-{}-{}_FW{}-{}-{}_".format(prefix,serial_number[0],serial_number[1],serial_number[2],serial_number[3], \
                                                          fw_version[0],fw_version[1],fw_version[2])
        timestemp =  str(time_now.tm_year)+time_sep+str(time_now.tm_mon)+time_sep+str(time_now.tm_mday)
        timestemp =  self._output_file + time_sep+str(time_now.tm_hour)+time_sep+str(time_now.tm_min)+time_sep+str(time_now.tm_sec)
        self._output_file += timestemp +".txt"
        self._writeToFile(self._output_file, {"time":timestemp} , mode="w")
        return self._output_file

    def dumpConfiguration( self, cfg, save_prev_data = True, save_compressed = True ):
        """Dump the configuration. Dumped data is stored to a file after calling dumpToJsonFile().
        The configuration is added to the log file if it was created.

        Args:
            cfg (dict): Configuration to be dumped
            save_prev_data (bool, optional): Set this to false if the previous dumped data should not be stored. Defaults to True.
            compressed (bool, optional): False for uncompressed, True for compressed in gz format. Defaults to True.
            
        """
        if save_prev_data:
            self.dumpToJsonFile(compressed=save_compressed)

        self._json_dump = {} # Note a new config will clear the old data
        self._json_dump["configuration"] = cfg

        if ( self._output_file != ""):
          self._writeToFile(self._output_file, cfg)

    def dumpLabSettings( self, settings):
        """Dump the labSettings. Dumped data is stored to a file after calling dumpToJsonFile().
        The settings are added to the log file if it was created.

        Args:
            settings (dict): Settings to be dumped
        """

        self._json_dump["lab_cfg"] = settings

        if ( self._output_file != ""):
          self._writeToFile(self._output_file, settings)
               
    def dumpInfo( self, info: dict):
        """ Dump the Info. Dumped data is stored to a file after calling dumpToJsonFile().
        The info is added to the log file if it was created.
        Args:
            info (dict): information to be logged
        """

        if "info" not in self._json_dump:
            self._json_dump["info"] = []

        info_to_append = copy.deepcopy(info)

        self._json_dump["info"].append(info_to_append)

        if ( self._output_file != ""):
          out = {"info": info}
          self._writeToFile(self._output_file, out)

    def dumpDevice(self, fw_version, serial_number):
        """ Dump the firmware version and the serial number.
        Dumped data is stored to a file after calling dumpToJsonFile().
        The data is added to the log file if it was created.

        Args:
            fw_version (bytearray): application id
            serial_number (int): serial number
        """
        device = {}
        device["fw_version"] = list(fw_version)
        device["serial"] = serial_number

        self._json_dump["device"] = device

        if ( self._output_file != ""):
            out = {"device":device}
            self._writeToFile(self._output_file, out)


    def dumpFrame(self, frame, measurement_info:dict=None ):
        """ Dump the frame. Dumped data is stored to a file after calling dumpToJsonFile().
        The data is added to the log file if it was created.

        Args:
            frame (bytearray): tmf8829 frame
            measurement_info (dict, optional): additional info for the measurement. Defaults to None.
        """
        fheader = tmf8829FrameHeader.from_buffer_copy( bytearray(frame)[Tmf8829AppCommon.PRE_HEADER_SIZE: \
                  Tmf8829AppCommon.PRE_HEADER_SIZE+ctypes.sizeof(struct__tmf8829FrameHeader)])      
        
        preheader = {}
        preheader["fifostatus"] = frame[0]
        preheader["systick"] = frame[1]+frame[2]*256+frame[3]*256*256+frame[4]*256*256*256
        frame_data = {}
        if measurement_info:
            frame_data["info"] = copy.deepcopy(measurement_info)
        frame_data["preheader"] = preheader
        fpMode = fheader.id & TMF8829_FPM_MASK
        if (fheader.id&TMF8829_FID_MASK) == TMF8829_FID_RESULTS:
            frame_data["header"] = ctypes2Dict(fheader)
            pixel_results=Tmf8829AppCommon.getPixelResultsFromFrame(frame, fpMode, fheader.layout)
            frame_data["resultdata"] = Tmf8829AppCommon.pixelResultsDeleteNoneParam(pixel_results)
            ffooter = tmf8829FrameFooter.from_buffer_copy( bytearray(frame)[-ctypes.sizeof(struct__tmf8829FrameFooter):]) 
            frame_data["footer"] = ctypes2Dict(ffooter)

        elif (fheader.id&TMF8829_FID_MASK) == TMF8829_FID_HISTOGRAMS:
            frame_data["header"] = ctypes2Dict(fheader)
            frame_refhisto =[]
            frame_histo = []
            referenceHistograms, mpHisto = Tmf8829AppCommon.getHistograms(frame, fpMode)
            
            for refHisto in referenceHistograms:
                frame_refhisto.append(ctypes2Dict(refHisto))
            frame_data["ref_histo"] = frame_refhisto

            for rawHisto in mpHisto:
                frame_histo_row = []
                for singlehisto in rawHisto:
                    frame_histo_row.append(ctypes2Dict(singlehisto))
                frame_histo.append(frame_histo_row)
            frame_data["mp_histo"] = frame_histo
            
            ffooter = tmf8829FrameFooter.from_buffer_copy( bytearray(frame)[-ctypes.sizeof(struct__tmf8829FrameFooter):]) 
            frame_data["footer"] = ctypes2Dict(ffooter)

        elif (fheader.id&TMF8829_FID_MASK) == TMF8829_FID_REF_SPAD_SCAN:
            refSp = tmf8829RefSpadFrame.from_buffer_copy( \
            bytearray(frame)[Tmf8829AppCommon.PRE_HEADER_SIZE:Tmf8829AppCommon.PRE_HEADER_SIZE+ctypes.sizeof(struct__tmf8829RefSpadFrame)])
            frame_data["ref_spad_scan"] = ctypes2Dict(refSp)

        else:
            frame_data["UNKNOWN"] = {"unknownframe"}

        if "frames" not in self._json_dump:
            self._json_dump["frames"] = []
        
        self._json_dump["frames"].append(frame_data)

        if ( self._output_file != ""):
            out = {"frame":frame_data}
            self._writeToFile(self._output_file, out)
 
    def dumpMeasurement(self, pixel_results:list=None, reference_pixel_histograms_HA:list=None, pixel_histograms_HA:list=None, \
                         reference_pixel_histograms:list=None, pixel_histograms:list=None, \
                        reference_spad_frames:list=None, measurement_info:dict=None):
        """Dump a Measurement Result 

        Args:
            pixel_results (list, optional): Pixel Results . Defaults to None.
            reference_pixel_histograms_HA (list, optional): Reference Pixel Histograms. 
                    Dual mode: Reference Pixel Histograms High Accuracy Range. Defaults to None.
            pixel_histograms_HA (list, optional): Pixel Histograms. Dual mode: Pixel Histograms High Accuracy Range. Defaults to None.
            reference_pixel_histograms (list, optional): Dual mode only: Reference Pixel Histograms regular/long range. Defaults to None.
            pixel_histograms (list, optional): Dual mode only: Pixel Histograms regular/long range. Defaults to None.
            reference_spad_frames (list, optional): Reference Spad Frame. Defaults to None.
            measurement_info (dict, optional): additional info for the measurement. Defaults to None.
        """
        frame_data = {}
        frame_refhisto_ha = []
        frame_histo_ha = []
        frame_refhisto = []
        frame_histo = []

        frame_refspadframe = []
        if measurement_info:
            frame_data["info"] = copy.deepcopy(measurement_info)

        if pixel_results:
            frame_data["results"] = pixel_results

        if reference_pixel_histograms:
            for refPixHisto in reference_pixel_histograms:
                frame_refhisto.append(ctypes2Dict(refPixHisto))
            frame_data["ref_histo"] = frame_refhisto

        if pixel_histograms:
            for rawPixelHisto in pixel_histograms:
                frame_histo_row = []
                for singlehisto in rawPixelHisto:
                    frame_histo_row.append(ctypes2Dict(singlehisto))
                frame_histo.append(frame_histo_row)
            frame_data["mp_histo"] = frame_histo

        if reference_pixel_histograms_HA:
            for refPixHisto in reference_pixel_histograms_HA:
                frame_refhisto_ha.append(ctypes2Dict(refPixHisto))
            frame_data["ref_histo_HA"] = frame_refhisto_ha

        if pixel_histograms_HA:
            for rawPixelHisto in pixel_histograms_HA:
                frame_histo_row = []
                for singlehisto in rawPixelHisto:
                    frame_histo_row.append(ctypes2Dict(singlehisto))
                frame_histo_ha.append(frame_histo_row)
            frame_data["mp_histo_HA"] = frame_histo_ha

        if reference_spad_frames:
            for refSpadFr in reference_spad_frames:
                refSp = tmf8829RefSpadFrame.from_buffer_copy( \
                bytearray(refSpadFr)[Tmf8829AppCommon.PRE_HEADER_SIZE:Tmf8829AppCommon.PRE_HEADER_SIZE+ctypes.sizeof(struct__tmf8829RefSpadFrame)])
                dictrefSp = ctypes2Dict(refSp.sum)
                frame_refspadframe.append(dictrefSp)
            frame_data["ref_spad"] = frame_refspadframe

        if "Result_Set" not in self._json_dump:
            self._json_dump["Result_Set"] = []
        
        self._json_dump["Result_Set"].append(frame_data)

        if ( self._output_file != ""):
            out = {"Result_Set":frame_data}
            self._writeToFile(self._output_file, out)

    def dumpToJsonFile(self, output_name = None, compressed:bool = True):
        """ The dumped data is written to a json file.

        Args:
            output_name (str, optional): Name of the json file. Defaults to None.
            compressed (bool, optional): False for uncompressed, True for compressed in gz format. Defaults to True.
        """
        if len(self._json_dump) == 0:
          return
        
        if (output_name == None):
            time_now = time.localtime()
            time_sep = "-"
            output_name = "{}_UID{}-".format("TMF8829",self._serial_number)
            timestemp =  str(time_now.tm_year)+time_sep+str(time_now.tm_mon)+time_sep+str(time_now.tm_mday)
            timestemp += time_sep+str(time_now.tm_hour)+time_sep+str(time_now.tm_min)+time_sep+str(time_now.tm_sec)
            output_name += timestemp +".json"
        
        same_file_name = 100
        save_output_name = os.path.join(os.path.join(os.path.dirname(sys.argv[0]),output_name))
        save_output_name_gz = os.path.join(os.path.join(os.path.dirname(sys.argv[0]),output_name + ".gz"))
        i = 0
        while (os.path.isfile(save_output_name) or os.path.isfile(save_output_name_gz)):
            index = output_name.find('.json')
            save_output_name = output_name[:index] + "_{}".format(i)+ output_name[index:]
            save_output_name_gz = save_output_name + ".gz"
            save_output_name = os.path.join(os.path.join(os.path.dirname(sys.argv[0]),save_output_name))
            save_output_name_gz = os.path.join(os.path.join(os.path.dirname(sys.argv[0]),save_output_name_gz))
            i=i+1
            if i >=  same_file_name:
                print("could not save file")
                break

        if compressed:
            TMF8829Logger._writeToFileCompressed(save_output_name, self._json_dump)
        else:
            TMF8829Logger._writeToFile(save_output_name, self._json_dump)

    @staticmethod
    def _writeToFile( output_file : str, data, mode = "a"):
        """ Write dictionary to the log File

        Args:
            output_file (str): log filename 
            data (dict): data in dictionary format
            mode (str, optional): file open mode. Defaults to "a".
        """
        filepathname = os.path.join(os.path.join(os.path.dirname(sys.argv[0]), output_file))

        with open(filepathname, mode) as f:
            json.dump(data, f, indent = 2)
            f.write('\n') # add a line break 
            f.close()

    @staticmethod
    def _writeToFileCompressed( output_file : str, data):
        """ Write dictionary to the log File

        Args:
            output_file (str): log filename 
            data (dict): data in dictionary format
        """
        filepathname = os.path.join(os.path.join(os.path.dirname(sys.argv[0]), output_file))

        with gzip.open(f"{filepathname}.gz", 'wt', encoding='UTF-8') as f:
            json.dump(data, f, indent = 2)
            f.write('\n') # add a line break 
            f.close()


    @staticmethod
    def patch_dict( dst: dict, patch: dict ) -> dict:
        """ Patch a nested dictionary. Does not support list patching! """
        for k, v in patch.items():
            if not isinstance(v, dict):
                dst[k] = v
            else:
                TMF8829Logger.patch_dict(dst[k], v)
