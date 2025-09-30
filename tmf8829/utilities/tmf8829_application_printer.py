# *****************************************************************************
# * Copyright by ams OSRAM AG                                                 *
# * All rights are reserved.                                                  *
# *                                                                           *
# *FOR FULL LICENSE TEXT SEE LICENSES-MIT.TXT                                 *
# *****************************************************************************
"""
   The printer class for the TMF8829 application.
"""

import __init__
from tmf8829_application_common import *

class Tmf8829ApplicationPrinter():
    """The printer class for the TMF8829 application.
    """
    @staticmethod
    def printFrame(frame:list, print_whole_frame=True, print_result_details = False):
        """ Functions that prints a result or histogram frame. 
        Args:
            frame (list[int]):  The frame that should be printed.
            print_whole_frame (bool, optional): If set to False only the header and footer content is printed. Defaults to True.
            print_result_details(bool, optional): If set the pixel results are printed with the parameter name. Defaults to False.
        """
        _header_size = ctypes.sizeof(struct__tmf8829FrameHeader)
        _footer_size = ctypes.sizeof(struct__tmf8829FrameFooter)
        _header = tmf8829FrameHeader.from_buffer_copy(bytearray(frame[
                  Tmf8829AppCommon.PRE_HEADER_SIZE:Tmf8829AppCommon.PRE_HEADER_SIZE+_header_size]))
        _footer = tmf8829FrameFooter.from_buffer_copy(bytearray(frame[-_footer_size:]))

        fpMode = _header.id & TMF8829_FPM_MASK
        if (print_whole_frame and (fpMode != None)):
            if (_header.id & TMF8829_FID_MASK ) == TMF8829_FID_RESULTS:
                results = Tmf8829AppCommon.getPixelResultsFromFrame(frame,fpMode,resultFormat=_header.layout)
                Tmf8829ApplicationPrinter.printResults(results, detailed=print_result_details)
            if (_header.id & TMF8829_FID_MASK ) == TMF8829_FID_HISTOGRAMS:
                ref_histo, histogram = Tmf8829AppCommon.getHistograms(frame, fpMode)
                Tmf8829ApplicationPrinter.printHistogram(ref_histo, histogram, full=True)

        _fifo_status = frame[0]
        _systick = frame[1]+frame[2]*256+frame[3]*256*256+frame[4]*256*256*256
        print( "FIFOSTATUS={} SYSTICK={} ".format( hex(_fifo_status),_systick),end="")
        print( "Header FID={} FPM={} Layout/Sub={} Payload={} FrameNumber={} bdv={} ".format(_header.id&TMF8829_FID_MASK, _header.id&TMF8829_FPM_MASK,hex(_header.layout),_header.payload,_header.fNumber,_header.bdv),end="")
        print( "Footer t0={} t1={} Status={} EOF={} ".format(_footer.t0Integration,_footer.t1Integration,_footer.frameStatus,_footer.eof))

    @staticmethod
    def printRefFrame(refFrame):
        """ Functions that prints a reference frame. 
        Args:
            refFrame (list): The reference frame that should be printed.
        """
        if not refFrame:
            print("no ref Frame available")
            return
        frame = tmf8829RefSpadFrame.from_buffer_copy(bytearray(refFrame)[Tmf8829AppCommon.PRE_HEADER_SIZE:])    # skip the pre-header
        
        print("Header FID={} FPM={} pl={} Payload={} FrameNumber={} bdv={} ".format(frame.header.id&TMF8829_FID_MASK, \
            frame.header.id&TMF8829_FPM_MASK, frame.header.layout, frame.header.payload, frame.header.fNumber, frame.header.bdv), end="")
        
        for sum in frame.sum:
            print( "[", end="")
            for s in sum:
                print("{},".format(s),end="")
            print("]",end="")
        print("Footer t0={} t1={} Status={} EOF={} ".format(frame.footer.t0Integration, frame.footer.t1Integration, frame.footer.frameStatus, frame.footer.eof))

    @staticmethod
    def printResults(results:list, detailed=False):
        """Function prints the result frame in tuples[x|y].

        Args:
            results (list): List (list[list[tuple[None,None,None]]]) with the results.
            detailed (bool, optional): If set the results are printed with the parameter name. Defaults to False.
        """
        print("Results: [y|x]")

        for x, rows in enumerate(results):
            for y, pixel in enumerate(rows):
                print("[{}|{}] ".format(y,x), end ="" )

                if pixel["noise"] != None:
                    print( "noise: " if detailed else "", pixel["noise"], end =" ", sep='' )

                if pixel["xtalk"] != None:
                    print( "xtalk:" if detailed else "", pixel["xtalk"], end =" ", sep='' )

                for p_nr, peak in enumerate(pixel["peaks"]):
                    if peak["distance"] != None:
                        print("Peak {}: (".format(p_nr) if detailed else "(",end ="" )
                        print( "distance:" if detailed else "", peak["distance"]/4, end =" ", sep='' )
                        print( "snr:" if detailed else "", repr(peak["snr"]), end ="", sep=''  )
                        if peak["signal"] != None:
                            print( "signal:" if detailed else " ", peak["signal"], end ="", sep='' )
                        print(")",end ="" )
                print("\n" if detailed else " ",end ="" )
            print("" if detailed else "\n",end ="" )
        print("\n")

    @staticmethod
    def printHistogram(ref_histogram:tmf8829Histogram, histogram, full=True):
        """Function that prints a raw = histogram frame
        Args:
            ref_histogram: the ref histogram 
            histogram: the list with the mp histograms
            full: print the full histogram data.
        """

        if ref_histogram:
            r = 0
            for col in ref_histogram:
                print()
                print( "[Ref{}]: ".format(r) ,end="")
                if full:
                    for bin in col.bin:
                        #print( "{} ".format(hex(bin)),end="")          # print all 64 bins
                        print( "{} ".format((bin)),end="")              # print all 64 bins
                else:
                    print ( "{:04}  ".format( (col[0]) ), end="")       # print only bin[0]=pixel index
                r += 1
            print()

        if histogram:
            r = 0
            for rows in histogram:
                print( )
                c=0
                for col in rows:
                    print( "MP[{:02}|{:02}]: ".format(c,r) ,end="")
                    if full:
                        for bin in col.bin:                             # print all 64/256 bins
                            # print( "{} ".format(hex(bin)),end="")
                            print( "{} ".format((bin)),end="")
                        print()
                    else:
                        print ( "{:04}  ".format( (col[0])), end="")    # print only bin[0]=pixel index
                    c += 1
                r += 1
            print()

