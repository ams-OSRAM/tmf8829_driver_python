# *****************************************************************************
# * Copyright by ams OSRAM AG                                                 *
# * All rights are reserved.                                                  *
# *                                                                           *
# *FOR FULL LICENSE TEXT SEE LICENSES-MIT.TXT                                 *
# *****************************************************************************
""" 
This example shows the funcionality of the TMF8829Logger in combination with the shield board evm.
Measurements are performed and stored in json files.
Optionaly measurements could be stored in a Log file in a txt format.
"""

import __init__
import time
import os

from __init__ import HEX_FILE
from utilities.tmf8829_logger_service import TMF8829Logger
from tmf8829_conv import *
from tmf8829_application import *
from tmf8829_config_page import *
from tmf8829_application_registers import *

###############################################################
## USER Settings
###############################################################
# Configuration could be done with here and is overwritten with the parameters in cfg.json.

default_logger_cfg = {
    "measure_cfg": {},
    "lab_cfg": {},
}

###################################################################################
## Example for the Tmf8829Logger 
###################################################################################
if __name__ == "__main__":

    logger = TMF8829Logger()
    
    #------------------------------------------------------------
    # Read in JSON files.
    #------------------------------------------------------------
    print("--- Read json file --- ")

    cfgFile  = os.path.dirname(__file__) + "\\cfg.json"
    cfg = logger.readCfgFile(cfgFile, default_logger_cfg)

    #------------------------------------------------------------
    # Check for available controller and update measurement config
    #------------------------------------------------------------
    if not isAmsEvmH5Available():
        print( f"No FTDI EVM and no H5 EVM found. Exiting." )
        quit(-1) 
        
    cfg["lab_cfg"]["use_spi"] = True
    
    #------------------------------------------------------------
    # Start the application
    #------------------------------------------------------------
    print("--- Start Application --- ")

    app = createTmf8829(use_spi=cfg["lab_cfg"]["use_spi"] )
    assert app.open()
    
    if not app.enable(send_wake_up_sequence=True):
        print("The application did not start up as expected")
        quit(-1)

    app.forceBootmonitor()
    if cfg["lab_cfg"]["use_spi"]:
        app.blCmdI2cOff()
    else:
        app.blCmdSpiOff()
    app.downloadAndStartApp(hex_file=HEX_FILE)

    appId = app.hal.txRx( [0], 4 )
    serial = app.readSerialNumber()

    #------------------------------------------------------------
    # Create a Log file.
    #------------------------------------------------------------
    try:
        outputFile = logger.createLogFile("Test", list(serial), [00,00,00])
    except:
       print("--- could not create log file --- ")
       time.sleep(5)
       quit (-1)
    
    #------------------------------------------------------------
    # Dump config into the file
    #------------------------------------------------------------
    print("--- Dump First Configuration and Start Measurement --- ")

    info = {}
    info["Config File"] = cfgFile

    logger.dumpConfiguration(cfg)
    logger.dumpInfo(info)
    #------------------------------------------------------------
    # Dump Firmware ID and Serial Number after Startup
    #------------------------------------------------------------
    print("[app_id, major, minor, patch] are: ", [f'0x{i:02x}' for i in appId ])
    deviceSerialNumber = int.from_bytes(bytes=serial, byteorder="little", signed=False)
    logger.dumpDevice(appId, deviceSerialNumber)

    #------------------------------------------------------------
    # Config the device 
    #------------------------------------------------------------
    app.configure(**cfg["measure_cfg"])       # use the parameters of the dict

    #------------------------------------------------------------
    # Start First Measurement and log the Frames 
    #------------------------------------------------------------
    num_of_measurements = 2

    app.startMeasure()

    for i in range(num_of_measurements):
        resf,hisf,reff = app.readMeasurementFrames()
        frames = resf+hisf+reff 
        for frame in frames:
            logger.dumpFrame(frame)
    
    app.stopMeasure()

    #------------------------------------------------------------
    # Start a Second Measurement and log the Frames
    #------------------------------------------------------------
    print("--- Dump Second Configuration and Start Measurement --- ")
    cfg2 = cfg
    cfg2["measure_cfg"]["fp_mode"] = app.FP_MODE_8x8B
    cfg2["measure_cfg"]["nr_peaks"] = 4
    cfg2["measure_cfg"]["noise_strength"] = 0
    cfg2["measure_cfg"]["publish"] = 1
    cfg2["measure_cfg"]["xtalk"] = 1
    cfg2["measure_cfg"]["signal_strength"] = 1

    logger.dumpConfiguration(cfg2,save_compressed=False) # new log file if config changes

    app.configure(**cfg2["measure_cfg"])
    
    app.startMeasure()

    for i in range(num_of_measurements):
        resf,hisf,reff = app.readMeasurementFrames()
        frames = resf+hisf+reff 
        for frame in frames:
            logger.dumpFrame(frame)

    app.stopMeasure()

    #------------------------------------------------------------
    # Start a third Measurement and log the combined Results
    #------------------------------------------------------------
    print("--- Dump Third Configuration and Start Measurement --- ")
    cfg3 = cfg
    cfg3["measure_cfg"]["fp_mode"] = app.FP_MODE_48x32
    cfg3["measure_cfg"]["nr_peaks"] = 1
    cfg3["measure_cfg"]["noise_strength"] = 1
    cfg3["measure_cfg"]["publish"] = 1
    cfg3["measure_cfg"]["xtalk"] = 1
    cfg3["measure_cfg"]["signal_strength"] = 1
    cfg3["measure_cfg"]["histograms"] = 1

    logger.dumpConfiguration(cfg3, save_compressed=False) # new log file if config changes

    app.configure(**cfg3["measure_cfg"])

    app.startMeasure()

    for i in range(num_of_measurements):
        resultFrame, histoFrames, refFrame = app.readMeasurementFrames()
        refhistogramResults, histogramResults = app.getAllHistogramResults(histoFrames)
        pixelResults = app.getFullPixelResult(frames=resultFrame)
        logger.dumpMeasurement(pixel_results=pixelResults, pixel_histograms=histogramResults, \
                               reference_pixel_histograms = refhistogramResults, reference_spad_frames= refFrame)

    app.stopMeasure()

    # ----------------------------------------
    # Stop Measurement and disable device
    # ----------------------------------------
    app.stopMeasure()
    app.disable()

    #------------------------------------------------------------
    # Dump to Json File
    #------------------------------------------------------------
    logger.dumpToJsonFile(compressed=False)
    
    print( "End" )
    time.sleep(0.5)
