# *****************************************************************************
# * Copyright by ams OSRAM AG                                                 *
# * All rights are reserved.                                                  *
# *                                                                           *
# *FOR FULL LICENSE TEXT SEE LICENSES-MIT.TXT                                 *
# *****************************************************************************
""" 
This example shows the funcionality of the Tmf8829ApplicationPrinter in combination with the shield board evm.
Measurements are performed and printed to the terminal.
Optionaly measurements could be stored in a Log file in a txt format.
"""
import __init__
import time

from __init__ import HEX_FILE
from utilities.tmf8829_application_printer import Tmf8829ApplicationPrinter as Tmf8829Printer
from tmf8829_conv import *
from tmf8829_application import *
from tmf8829_config_page import *
from tmf8829_application_registers import *

###################################################################################
## User Config
###################################################################################
use_spi = True
precfg = Tmf8829AppRegs.TMF8829_CMD_STAT._cmd_stat._CMD_LOAD_CFG_16X16
num_of_measurements = 2
use_iterations = 2000

results3dcorrected = True
resultsInXYZ = True

###################################################################################
## Example for the Tmf8829Logger 
###################################################################################
if __name__ == "__main__":

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
    # Configuration
    #------------------------------------------------------------
    app.configure(histograms=1, iterations=use_iterations, publish = 1)
    app.preConfigure(cmd=precfg)

    #------------------------------------------------------------
    # Print Frames
    #------------------------------------------------------------
    print ("---Print Frames---")
    app.startMeasure()
    resultFrame, histoFrames, refFrame = app.readMeasurementFrames()
    app.stopMeasure()
    for frame in histoFrames:
        Tmf8829Printer.printFrame(frame=frame,print_whole_frame=False)
    for frame in resultFrame:
        Tmf8829Printer.printFrame(frame=frame,print_whole_frame=False)
    for frame in refFrame:
        Tmf8829Printer.printRefFrame(frame)

    #------------------------------------------------------------
    # Print whole Frames
    #------------------------------------------------------------
    print ("--- Print Print whole Frames ---")
    app.startMeasure()
    resultFrame, histoFrames, refFrame = app.readMeasurementFrames()
    app.stopMeasure()
    for frame in histoFrames:
        Tmf8829Printer.printFrame(frame=frame,print_whole_frame=True)
    for frame in resultFrame:
        Tmf8829Printer.printFrame(frame=frame,print_whole_frame=True)
    for frame in refFrame:
        Tmf8829Printer.printRefFrame(frame)
    
    #------------------------------------------------------------
    # Print Result Details
    #------------------------------------------------------------
    print ("--- Print Result Details ---")
    app.startMeasure()
    resultFrame, histoFrames, refFrame = app.readMeasurementFrames()
    app.stopMeasure()
    for frame in resultFrame:
        Tmf8829Printer.printFrame(frame=frame, print_whole_frame=True, print_result_details=True)

    #------------------------------------------------------------
    # Disable
    #------------------------------------------------------------
    app.disable()

    print( "End" )
    time.sleep(0.5)

