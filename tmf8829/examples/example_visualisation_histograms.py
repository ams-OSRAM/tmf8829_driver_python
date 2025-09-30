# *****************************************************************************
# * Copyright by ams OSRAM AG                                                 *
# * All rights are reserved.                                                  *
# *                                                                           *
# *FOR FULL LICENSE TEXT SEE LICENSES-MIT.TXT                                 *
# *****************************************************************************
""" 
This is an example with the shield board evm.
Measurements are performed and histograms are visualised.
"""
import __init__ 
import time
import matplotlib.pyplot as plt

from __init__ import HEX_FILE
from tmf8829_conv import *
from tmf8829_application import Tmf8829Application
from utilities.tmf8829_visualisation import Tmf8829PlotHistograms, Pixel

###################################################################################
## User Config
###################################################################################
_use_spi = True
_fpMode = Tmf8829Application.FP_MODE_16x16
_use_iterations = 500
_use_period = 1
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
    app.configure(period=_use_period,fp_mode=_fpMode, histograms=1,iterations=_use_iterations)
    
    #------------------------------------------------------------
    # Choose Pixels and Create empty Plot
    #------------------------------------------------------------
    # Note Pixel(column, row)!!!
    fpPixels = []
    fpPixels.append(Pixel(2, 2))
    fpPixels.append(Pixel(6, 6))
    if _fpMode >= Tmf8829Application.FP_MODE_16x16:
        fpPixels.append(Pixel(13, 13))

    refPixels = []
    refPixels.append(Pixel(1,1))
    
    subplotsFpPixel, subplotsRefPixel = Tmf8829PlotHistograms.createEmptyPlot(Tmf8829Application.binsPerHistograms(_fpMode), 64, fpPixels, refPixels)

    #------------------------------------------------------------
    # Measurement and Visualisation
    #------------------------------------------------------------
    app.startMeasure()
    while plt.fignum_exists(1):
        resultFrame, histoFrames, refFrame = app.readMeasurementFrames()

        refhistogramResults, histogramResults = app.getAllHistogramResults(histoFrames)

        if (len(refhistogramResults)) > 0:
            Tmf8829PlotHistograms.updateHistogramPlot( refhistogramResults, histogramResults, subplotsFpPixel, subplotsRefPixel)
            plt.pause(0.01)

    #------------------------------------------------------------
    # Disable
    #------------------------------------------------------------
    app.stopMeasure()
    app.disable( )
    app.close()

    print( "End" )
    time.sleep(0.5)

