# *****************************************************************************
# * Copyright by ams OSRAM AG                                                 *
# * All rights are reserved.                                                  *
# *                                                                           *
# *FOR FULL LICENSE TEXT SEE LICENSES-MIT.TXT                                 *
# *****************************************************************************

"""Plots an intensity map for all SPADs of the focal plane and the reference macropixels. """

import __init__

import sys
import numpy as np
import matplotlib.pyplot as plt
import collections

from tmf8829_application import Tmf8829Application
from  tmf8829_application_defines import tmf8829RefSpadFrame

Pixel = collections.namedtuple("Pixel", ["x", "y"])

class Tmf8829PlotPixelMap():
    """The TMF8829 visualisation class for the Pixel Map.
    """
    def createEmptyPixelMapPlot(columns: int = Tmf8829Application.MP_FOV_COLUMNS , rows:int = Tmf8829Application.MP_FOV_ROWS):
        """Sets up the plot and shows it with blank data."""
        plt.figure(figsize=(16, 8))
        gs = plt.GridSpec(2, 2, width_ratios=[2, 1])

        axFpPixel = plt.subplot(gs[:, 0])
        axFpPixel.set_title("Focal Plane")
        imFpPixel = axFpPixel.imshow(np.zeros((rows, columns), dtype="int64"))
        imFpPixel.set_visible(False)
        plt.colorbar(imFpPixel)

        axRefPixelT0 = plt.subplot(gs[0, 1])
        axRefPixelT0.set_title("Reference (T0)")
        imRefPixelT0 = axRefPixelT0.imshow(np.zeros((Tmf8829Application.REF_PIXEL_ROWS , Tmf8829Application.REF_PIXEL_COLUMNS ), dtype="int64"))
        imRefPixelT0.set_visible(False)
        plt.colorbar(imRefPixelT0)

        axRefPixelT1 = plt.subplot(gs[1, 1])
        axRefPixelT1.set_title("Reference (T1)")
        imRefPixelT1 = axRefPixelT1.imshow(np.zeros((Tmf8829Application.REF_PIXEL_ROWS , Tmf8829Application.REF_PIXEL_COLUMNS ), dtype="int64"))
        imRefPixelT1.set_visible(False)
        plt.colorbar(imRefPixelT1)

        plt.show(block=False)

        return (imFpPixel, imRefPixelT0, imRefPixelT1)

    def updatePixelMapPlot( imFpPixel, imRefPixelT0, imRefPixelT1,pixelArray, refPixel: tmf8829RefSpadFrame):  # pylint: disable=too-many-locals
        """Updates the images in a plot using data from the sub-measurements."""

        fpPixelImage = np.zeros((len(pixelArray), len(pixelArray[0])), dtype="int64")
        refPixelT0Image = np.zeros((Tmf8829Application.REF_PIXEL_ROWS, Tmf8829Application.REF_PIXEL_COLUMNS ), dtype="int64")
        refPixelT1Image = np.zeros((Tmf8829Application.REF_PIXEL_ROWS, Tmf8829Application.REF_PIXEL_COLUMNS ), dtype="int64")

        for y, column in enumerate(pixelArray):
            for x, pixel in enumerate(column):
                fpPixelImage[y,x] = pixel["noise"]

        refPixelT0Image[0,0] = refPixel.sum[0][0]
        refPixelT0Image[0,1] = refPixel.sum[0][1]
        refPixelT0Image[1,0] = refPixel.sum[0][2]
        refPixelT0Image[1,1] = refPixel.sum[0][3]
        refPixelT1Image[0,0] = refPixel.sum[1][0]
        refPixelT1Image[0,1] = refPixel.sum[1][1]
        refPixelT1Image[1,0] = refPixel.sum[1][2]
        refPixelT1Image[1,1] = refPixel.sum[1][3]

        imFpPixel.set_data(fpPixelImage)
        imRefPixelT0.set_data(refPixelT0Image)
        imRefPixelT1.set_data(refPixelT1Image)
        for _ in range(2):
            # The limits apparently only update when set_clim() is called twice.
            imFpPixel.set_clim(np.min(fpPixelImage), np.max(fpPixelImage))
            imRefPixelT0.set_clim(np.min(refPixelT0Image), np.max(refPixelT0Image))
            imRefPixelT1.set_clim(np.min(refPixelT1Image), np.max(refPixelT1Image))
        imFpPixel.set_visible(True)
        imRefPixelT0.set_visible(True)
        imRefPixelT1.set_visible(True)

class Tmf8829PlotHistograms():
    """The TMF8829 visualisation class for the Mp and Ref Mp histograms.
    """
    BAR_WIDTH = 0.8
    XTICKS_INCREMENT_DEFAULT = 5
    XTICKS_INCREMENT_256_BINS = 20

    def createEmptyPlot(numFpPixelBins, numRefPixelBins, fpPixels, refPixels):
        # pylint: disable=disallowed-name
        """Sets up the plot and shows it with blank data."""
        if len(fpPixels) == 0 and len(refPixels) == 0:
            raise ValueError("At least one focal plane pixel or reference pixel must be plotted")
        if len(fpPixels) != len(set(fpPixels)):
            raise ValueError("Focal plane pixels contain duplicates")
        if len(refPixels) != len(set(refPixels)):
            raise ValueError("Reference pixels contain duplicates")

        subplotsFpPixel = {}
        subplotsRefPixel = {}

        fig, axs = plt.subplots(nrows=len(fpPixels) + len(refPixels), ncols=1)

        # Add extra space for subplot titles to fit
        fig.subplots_adjust(hspace=1.0)

        # Terminate process when the plot window is closed via event handler (when updating plot while plt.fignum_exists(1),
        # a deadlock was sometimes observed after window closure)
        def onClose(_):
            sys.exit()
        fig.canvas.mpl_connect('close_event', onClose)

        # Perform initial setup of histogram subplots
        def setupSubplot(ax, numBins, title):
            ax.set_title(title)
            xticks = list(range(0, numBins, Tmf8829PlotHistograms.XTICKS_INCREMENT_256_BINS if numBins == 256 else Tmf8829PlotHistograms.XTICKS_INCREMENT_DEFAULT))
            if xticks[-1] != numBins - 1:
                xticks.append(numBins - 1)
            ax.set_xticks(xticks)
            ax.set_xlim(-Tmf8829PlotHistograms.BAR_WIDTH / 2.0 - (1.0 - Tmf8829PlotHistograms.BAR_WIDTH), float(numBins) - 1.0 \
                        + Tmf8829PlotHistograms.BAR_WIDTH / 2.0 + (1.0 - Tmf8829PlotHistograms.BAR_WIDTH))
            ax.set_yticks([])
            return ax.bar(range(numBins), [0] * numBins, width=Tmf8829PlotHistograms.BAR_WIDTH)
        for index, pixel in enumerate(fpPixels):
            ax = axs[index]
            bar = setupSubplot(ax, numFpPixelBins, f"Focal Plane Pixel ({pixel[0]},{pixel[1]})")
            subplotsFpPixel[pixel] = (ax, bar)
        for index, pixel in enumerate(refPixels):
            ax = axs[len(fpPixels) + index]
            bar = setupSubplot(ax, numRefPixelBins, f"Reference Pixel ({pixel.x},{pixel.y})")
            subplotsRefPixel[pixel] = (ax, bar)

        plt.show(block=False)

        return subplotsFpPixel, subplotsRefPixel

    def updateHistogramPlot(refhistogramResults, histogramResults, subplotsFpPixel, subplotsRefPixel):
        # pylint: disable=disallowed-name
        """Updates the plot with histogram data from the frame container."""
        def updateSubplot(ax, bar, histogram):
            for index, value in enumerate(histogram):
                bar[index].set_height(value)
            max_value = max(histogram)
            ax.set_ylim(0.0, max_value)
            ax.set_yticks([0.0, max_value])
        for pixel, (ax, bar) in subplotsFpPixel.items():
            updateSubplot(ax, bar, histogramResults[pixel.y][pixel.x].bin)
        for pixel, (ax, bar) in subplotsRefPixel.items():
            refP=0+4
            if pixel.x == 1 and pixel.y == 0:
                refP = 1+4
            elif pixel.x == 0 and pixel.y == 1:
                refP = 2+4
            elif pixel.x == 1 and pixel.y == 1:
                refP = 3+4

            updateSubplot(ax, bar, refhistogramResults[refP].bin)

if __name__ == "__main__":
    print("Visualisation class for tmf8829")
