# *****************************************************************************
# * Copyright by ams OSRAM AG                                                 *
# * All rights are reserved.                                                  *
# *                                                                           *
# *FOR FULL LICENSE TEXT SEE LICENSES-MIT.TXT                                 *
# *****************************************************************************
""" 
This example shows the funcionality of the TMF8829Logger in combination with the shield board evm.
Measurements in dual mode are performed and stored in json files.
"""

import __init__
import time

from __init__ import HEX_FILE
from utilities.tmf8829_logger_service import TMF8829Logger
from tmf8829_conv import *
from tmf8829_application import *
from tmf8829_config_page import *
from tmf8829_application_registers import *
from register_page_converter import RegisterPageConverter as RegConv

###################################################################################
## User Config
###################################################################################
use_spi = True
num_of_measurements = 1
use_histograms = 1
use_iterations = 500

results3dcorrected = False
resultsInXYZ = True
###################################################################################
## Example for the Tmf8829Logger 
###################################################################################
if __name__ == "__main__":

    logger = TMF8829Logger()
    
    #------------------------------------------------------------
    # Start the application
    #------------------------------------------------------------
    app = createTmf8829(use_spi=use_spi )
    assert app.open()
    
    if not app.enable(send_wake_up_sequence=True):
        print("The application did not start up as expected")
        quit(-1)

    app.forceBootmonitor()
    if use_spi:
        app.blCmdI2cOff()
    else:
        app.blCmdSpiOff()
    app.downloadAndStartApp(hex_file=HEX_FILE)

    appId = app.hal.txRx( [0], 4 )
    serial = app.readSerialNumber()
    deviceSerialNumber = int.from_bytes(bytes=serial, byteorder="little", signed=False)

    print("[app_id, major, minor, patch] are: ", [f'0x{i:02x}' for i in appId ])

    #------------------------------------------------------------
    # List of Configurations
    #------------------------------------------------------------
    precfgs = [ Tmf8829AppRegs.TMF8829_CMD_STAT._cmd_stat._CMD_LOAD_CFG_8X8,
                Tmf8829AppRegs.TMF8829_CMD_STAT._cmd_stat._CMD_LOAD_CFG_8X8_LONG_RANGE,
                Tmf8829AppRegs.TMF8829_CMD_STAT._cmd_stat._CMD_LOAD_CFG_16X16,
                Tmf8829AppRegs.TMF8829_CMD_STAT._cmd_stat._CMD_LOAD_CFG_32X32,
                Tmf8829AppRegs.TMF8829_CMD_STAT._cmd_stat._CMD_LOAD_CFG_48X32]
    
    app.configure(histograms=use_histograms, iterations=use_iterations, dual_mode=1)

    for precfg in precfgs:
        print(" --- Pre Configuration: {} --- ".format(precfg) )
        app.preConfigure(cmd=precfg)
        
        cfg = app.loadConfig()
        cfg_dict = RegConv.readPageToDict(cfg, Tmf8829ConfigRegs())     # convert bytestream to dictionary

        logger.dumpConfiguration(cfg_dict,save_compressed=False)
        logger.dumpDevice(appId, deviceSerialNumber)

        app.startMeasure()

        for i in range(num_of_measurements):

            histogramResults = []
            refhistogramResults = []
            histogramResultsHA = []
            refhistogramResultsHA = []    

            resultFrame, histoFrames, refFrame = app.readMeasurementFrames()
            
            pixelResults = app.getFullPixelResult(frames=resultFrame, toMM=True, pointCloud=results3dcorrected, distanceToXYZ= resultsInXYZ)

            if use_histograms:
                refhistogramResultsHA, histogramResultsHA, \
                refhistogramResults, histogramResults = Tmf8829Application.getAllHistogramResultsDualMode(histoFrames)

                logger.dumpMeasurement( pixel_results = pixelResults, reference_spad_frames = refFrame, \
                                        pixel_histograms = histogramResults, reference_pixel_histograms = refhistogramResults, \
                                        pixel_histograms_HA = histogramResults, reference_pixel_histograms_HA = refhistogramResults )
                                
                
            else:
                logger.dumpMeasurement(pixel_results=pixelResults)

        app.stopMeasure()

    #------------------------------------------------------------
    # Dump to Json File
    #------------------------------------------------------------
    logger.dumpToJsonFile(compressed=False)

    app.disable()
    
    print( "End" )
    time.sleep(0.5)

