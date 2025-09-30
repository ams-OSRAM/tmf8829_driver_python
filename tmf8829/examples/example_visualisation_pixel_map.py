# *****************************************************************************
# * Copyright by ams OSRAM AG                                                 *
# * All rights are reserved.                                                  *
# *                                                                           *
# *FOR FULL LICENSE TEXT SEE LICENSES-MIT.TXT                                 *
# *****************************************************************************
""" 
This example shows the visualisation of an intensity map with the shield board evm.
Measurements are performed and a pixel map is plotted.
"""
import __init__ 
import time
import matplotlib.pyplot as plt

from __init__ import HEX_FILE
from tmf8829_conv import *
from tmf8829_application import Tmf8829Application
from tmf8829_application_defines import tmf8829RefSpadFrame
from utilities.tmf8829_visualisation import Tmf8829PlotPixelMap

###################################################################################
## User Config
###################################################################################
_use_spi = True
_fpMode = Tmf8829Application.FP_MODE_32x32
_use_iterations = 500
_use_period = 100
###################################################################################
## Example for the Histogram Visualisation 
###################################################################################
if __name__ == "__main__":

    #------------------------------------------------------------
    # Start the application
    #------------------------------------------------------------
    app = createTmf8829(use_spi=_use_spi )
    assert app.open()
    
    if not app.enable(send_wake_up_sequence=True):
        print("The application did not start up as expected")
        quit(-1)

    app.forceBootmonitor()
    if _use_spi:
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
    app.configure(period=_use_period,fp_mode=_fpMode,nr_peaks=0, noise_strength=1, full_noise=1, publish=1, iterations=_use_iterations)
    
    #------------------------------------------------------------
    # Create empty Plot
    #------------------------------------------------------------
    columns = Tmf8829Application.pixelColumns(_fpMode)
    rows = Tmf8829Application.pixelRows(_fpMode)
    imFpPixel, imRefPixelT0, imRefPixelT1 = Tmf8829PlotPixelMap.createEmptyPixelMapPlot(columns, rows)

    #------------------------------------------------------------
    # Measurement and Visualisation
    #------------------------------------------------------------
    app.startMeasure()
    for _ in range(1000):
        resultFrame, histoFrames, refFrame = app.readMeasurementFrames()
        pixelResults = app.getFullPixelResult(resultFrame)
        refframe = tmf8829RefSpadFrame.from_buffer_copy(refFrame[0])
        Tmf8829PlotPixelMap.updatePixelMapPlot(imFpPixel, imRefPixelT0, imRefPixelT1, pixelResults, refframe)
        plt.pause(0.01)

    #------------------------------------------------------------
    # Disable
    #------------------------------------------------------------
    app.stopMeasure()
    app.disable( )
    app.close()

    print( "End" )
    time.sleep(0.5)

