# *****************************************************************************
# * Copyright by ams OSRAM AG                                                 *
# * All rights are reserved.                                                  *
# *                                                                           *
# *FOR FULL LICENSE TEXT SEE LICENSES-MIT.TXT                                 *
# *****************************************************************************
"""
The TMF8829 application class for the Shield Evm Board.
"""

import __init__
import time

from tmf8829_application_common import *
from tmf8829_bootloader import Tmf8829Bootloader
from aos_com.hal_register_io import HalRegisterIo
from register_page_converter import RegisterPageConverter

# additional interrupt bits 
TMF8829_INT_MOTION      = 0x02  # motion interrupt bit
TMF8829_INT_PROXIMITY   = 0x04  # proximity interrupt bit

class Tmf8829Application(Tmf8829Bootloader, Tmf8829AppCommon):
    """The TMF8829 application class for the Shield Evm Board.
    """
    
    VERSION = 1.12
    """Version log
    - 1.0 First  version
    - 1.1 add FP mode 48x32
    - 1.2 configuration page and diagnostic page changed a lot
    - 1.3 printing of frame content removed
    - 1.4 
    - 1.5 configure and writeDiagnostics parameters Name changed
    - 1.6 added config-byte-stream to dict and diag-byte-stream to dict
    - 1.7 added power modes
    - 1.8 added calibration page
    - 1.9 added info parameter readout
    - 1.10 added support for dual mode
    - 1.11 splitted up tmf8829_application to tmf8829_application_common and tmf8829_application
    - 1.12 support for motion detection and proximity 
    """

    def __init__(self, hal:HalRegisterIo, gpio_hal:HalRegisterIo=None ):
        """The default constructor. It sets default values for the internal variables.
        Args:
            hal (HalRegisterIo): The communication class instance to talk i2c or spi .
            gpio_hal (HalRegisterIo): The communication class instance for gpio.
        """
        super().__init__(hal=hal, gpio_hal=gpio_hal)
        self.cfg_fpMode = Tmf8829Application.FP_MODE_16x16
        self.cfg_resultFormat = 1 # 1 peak, no noise, no xtalk etc. 0x3C    # maximum amount of information
        self.cfg_histograms = 0 
        self.cfg_refFrame = 0
        self.cfg_dualMode = 0
        self.cfg_powerMode = -1 # undefined power mode, check with device

    def numberOfFramesPerMeasurement(self):
        """Number of frames that complete one measurement, and takes into account if raw histogram frames are produced or 
           if reference frames are produced too. (8x8, 16x16, 32x32, 48x32)
        Return:
            int: number of frames of one measurement set
        """
        _frames = 1
        _histograms = 2
        _refs = 0
        if self.cfg_fpMode > Tmf8829Application.FP_MODE_16x16:
            _histograms = 8        # 32x32 has 8
            _frames += 1            # two results
        if self.cfg_fpMode == Tmf8829Application.FP_MODE_48x32:
            _histograms = 12        # 48x32 has 12
            
        if not self.cfg_histograms:
            _histograms = 0

        if self.cfg_refFrame:
            _refs = _frames
        
        if self.cfg_dualMode == 1:
            _histograms = _histograms*2

        return _frames + _histograms + _refs

    def readSerialNumber(self) -> bytes:
        """Function to read the serial number.
        Return:
               bytes: the four serial number bytes
        """
        serial_number = self.hal.txRx([Tmf8829AppRegs.TMF8829_SERIAL_NUMBER_0.addr], 4 )
        return serial_number

    def softReset(self, use_spi:bool):
        """Function performs a soft-reset = very close to a power-up reset, as the HW is reinitialized as are
        internal data structures. The I3C dynamic addressing however stays as before the reset

        Args:
            use_spi (bool): True for spi, False for i2c.
        """        

        self.io.regWrite( self.reg.ENABLE, poff=0, pon=1, powerup_select = self.reg.ENABLE._powerup_select._FORCE_BOOTMONITOR )   # make sure that we induce a force to ram self after reset
        time.sleep(0.003)
        self.io.regWrite( self.reg.RESET, soft_reset=1 )
        time.sleep(0.003)
        if use_spi:
            self.blCmdI2cOff()            
        else:
            self.blCmdSpiOff()                                                                                      
        self.blCmdStartRamApp(app_id=1) 
        self.io.regWrite( self.reg.ENABLE, powerup_select = self.reg.ENABLE._powerup_select._RAM )                 # make sure that we wakeup properly from standby-timed

    def startMeasure(self):
        """Function to clean-up pending interrupts, enable interrupts and start a new measurement
        Return:
            int: the read-back response
        """
        self.clearIntStatus( 0xFF )                                     # clear any old pending interrupts
        self.enableInt( TMF8829_INT_RESULTS | TMF8829_INT_HISTOGRAMS )  # enable interrupts that are interesting 
        return self.sendCommand(cmd=Tmf8829AppRegs.TMF8829_CMD_STAT._cmd_stat._CMD_MEASURE)

    def stopMeasure(self):
        """Function to stop measurements, clean-up pending interrupts, disable interrupts 
        Return:
            int: the read-back response
        """
        self.enableInt( 0 )                                             # disable all interrupts  
        self.clearIntStatus( 0xFF )                                     # clear any old pending interrupts
        return self.sendCommand(cmd=Tmf8829AppRegs.TMF8829_CMD_STAT._cmd_stat._CMD_STOP, wait_only_for_ok=True)

    def preConfigure(self, cmd):
        """Function to perform a pre configuration.
        Args:
            cmd(int): byte representing the command CMD_LOAD_CFG_8X8 to CMD_LOAD_CFG_48X32_HIGH_ACCURACY
        Return:
            int: the read-back response
        """
        
        if (cmd >= Tmf8829AppRegs.TMF8829_CMD_STAT._cmd_stat._CMD_LOAD_CFG_8X8) and \
            (cmd <= Tmf8829AppRegs.TMF8829_CMD_STAT._cmd_stat._CMD_LOAD_CFG_8X8_HIGH_ACCURACY):
            self.cfg_fpMode = 0 
        elif (cmd >= Tmf8829AppRegs.TMF8829_CMD_STAT._cmd_stat._CMD_LOAD_CFG_16X16) and \
            (cmd <= Tmf8829AppRegs.TMF8829_CMD_STAT._cmd_stat._CMD_LOAD_CFG_16X16_HIGH_ACCURACY):
            self.cfg_fpMode = 2
        elif (cmd >= Tmf8829AppRegs.TMF8829_CMD_STAT._cmd_stat._CMD_LOAD_CFG_32X32) and \
            (cmd <= Tmf8829AppRegs.TMF8829_CMD_STAT._cmd_stat._CMD_LOAD_CFG_32X32_HIGH_ACCURACY):
            self.cfg_fpMode = 3 
        elif (cmd >= Tmf8829AppRegs.TMF8829_CMD_STAT._cmd_stat._CMD_LOAD_CFG_48X32) and \
            (cmd <= Tmf8829AppRegs.TMF8829_CMD_STAT._cmd_stat._CMD_LOAD_CFG_48X32_HIGH_ACCURACY):
            self.cfg_fpMode = 5
        else:
            raise("Wrong pre configuration".format(cmd))
        
        return self.sendCommand(cmd=cmd)

    def sendCommand(self,cmd=Tmf8829AppRegs.TMF8829_CMD_STAT._cmd_stat._CMD_MEASURE, timeout:float=1.5, wait_only_for_ok:bool=False):
        """Function to execute an application command.

        Args:
            cmd (int, optional): Byte representing the command. Defaults to Tmf8829AppRegs.TMF8829_CMD_STAT._cmd_stat._CMD_MEASURE.
            timeout (float, optional): How long to poll for a response, before giving up. Defaults to 1.5.
            wait_only_for_ok (bool, optional): Status command Tmf8829AppRegs.TMF8829_CMD_STAT._cmd_stat._STAT_OK expected. Defaults to False.

        Returns:
            int: the read-back response
        """

        self.hal.tx( Tmf8829AppRegs.TMF8829_CMD_STAT.addr, [ cmd ] )
        _max_time = time.time() + timeout
        while True:
            _resp = self.hal.txRx([Tmf8829AppRegs.TMF8829_CMD_STAT.addr], 2 ) # read back also previous command
            if len(_resp) and _resp[0] < Tmf8829AppRegs.TMF8829_CMD_STAT._cmd_stat._CMD_MEASURE:
                if _resp[0] > Tmf8829AppRegs.TMF8829_CMD_STAT._cmd_stat._STAT_ACCEPTED:
                    raise Exception( "Error command {} failed with {}".format( cmd, _resp[0] ) )
                else:
                    if wait_only_for_ok:
                        if _resp[0] == Tmf8829AppRegs.TMF8829_CMD_STAT._cmd_stat._STAT_OK:
                            return list(_resp)
                    else:                           # return also in case of _STAT_ACCEPTED
                        return list(_resp)
            if time.time() > _max_time:
                raise Exception( "Error command {} timeout".format( cmd ))

    def configure(self, period:int = None, iterations:int = None, fp_mode:int = None, spad_select:int = None, ref_spad_select:int = None, dead_time:int = None,
                  nr_peaks:int = None, signal_strength:bool = None, noise_strength:bool = None, xtalk:bool = None,
                  full_noise:bool = None, histograms:int = None, publish:int = None, bdv_temp_sensor:int = None,
                  t0_vcsel:int = None, t1_vcsel:int = None, dither_increment:int = None, dither_rounds:int = None, pulse_width:int = None, ext_clk_input:int = None,
                  current:int = None, hi_len:int = None, ext_en_output:int = None, ext_inv_output:int = None, vcsel_period:int = None, vcdrv_offset:int = None,
                  vc_spr_spec_single_edge:int=None,vc_spr_spec_cfg:int=None,vc_spr_spec_amp:int=None,
                  histogram_bins:int = None, bin_shift:int = None,ref_bin_shift:int = None, tdc_offset:int = None, settling:int = None,
                  peak_bins:int= None, ref_peak_bins:int = None, select:int = None, confidence_threshold:int = None,
                  signal_level:int= None, poisson:int= None, peak_detect_start:int= None, min_distance_uq:int= None, parameter_a:int= None, parameter_b:int= None,
                  xtalk_distance_mm:int=None, xtalk_max:int=None, xtalk_edge:int=None,
                  int_zone_mask:list = None, int_threshold_low:int = None, int_threshold_high:int = None, int_persistence:int = None, post_processing:int = None,
                  gpio0:int=None, gpio1:int=None, gpio2:int=None, gpio3:int=None, gpio4:int=None, gpio5:int=None, gpio6:int=None, pre_delay:int = None, 
                  cpu_sleep:int=None, device_sleep:int=None,lp_osc_device_sleep:int=None,spad_cropping:int=None,
                  spr_spec_single_edge:int=None,spr_spec_cfg:int=None,spr_spec_amp:int=None, add_100_mm_offset:int=None,
                  mp_top_x:int=None, mp_top_y:int=None, mp_bottom_x:int=None, mp_bottom_y:int=None, ref_mp:int=None ,
                  motion_distance:int=None, detect_snr:int=None, release_snr:int=None, motion_adjacent:int=None,
                  dual_mode:int=None, high_accuracy_iterations:int=None, prox_distance:int=None ):
        """Function to reconfigure the device.
           The config page is loaded with the CMD_LOAD_CONFIG_PAGE command.
           The config registers are modified and the new config page is written with the CMD_WRITE_PAGE command.
        Args:
            period(int, optional): period in milliseconds. set to 0 for single shot. Defaults to None.
            iterations(int, optional): iterations is multiplied by 1024. Defaults to None.
            fp_mode(int, optional): set to Tmf8829Application.FP_MODE__16x16, or one of the other modes. Defaults to None.
            spad_select(int, optional): 6-bit mask representing the spad to be selected per MP (in 8x8 and 16x16 mode only). Defaults to None.
            ref_spad_select(int, optional): SPAD mask per Ref pixel is the same for all RefPixel. Defaults to None.
            dead_time(int, optional):  SPAD dead time setting. Defaults to None.
            nr_peaks(int, optional): range is 0..4 (how many peaks shall be reported per MP). Defaults to None.
            signal_strength(bool, optional): if set do report peak strength with each peak. Defaults to None.
            noise_strength(bool, optional): if set do report the averaged noise level per MP. Defaults to None.
            xtalk(bool, optional): if set do report the xtalk per MP. Defaults to None.
            full_noise(bool, optional): if set to non-zero the sum instead of the noise/bins will be reported in the noise field of results. Defaults to None.
            histograms(int, optional): if set do report raw histograms (=blocking mode). Defaults to None.
            publish(int, optional): publish the SUM per Reference pixel at address 0x20. Defaults to None.
            bdv_temp_sensor(int, optional): temperature sensors for BDV decision. Defaults to None.
            t0_vcsel(int, optional): Set to 0 to use no VCSEL, set to 1 to use VCSEL0, set to 2 to use VCSEL1. Defaults to None.
            t1_vcsel(int, optional): Set to 0 to use no VCSEL, set to 1 to use VCSEL0, set to 2 to use VCSEL1. Defaults to None.
            dither_increments(int, optional): Add this many unit delays every VCSEL period. Defaults to None.
            dither_rounds(int, optional): Dither rounds, number of VCSEL periods to apply increment . Defaults to None.
            pulse_width(int, optional): vcsel driver pulse width  . Defaults to None.
            ext_clk_input(int, optional): use an external clock for VCDRV. Defaults to None.
            current(int, optional): vcsel driver current. Defaults to None.
            hi_len(int, optional): length of vcdrv high-pulse . Defaults to None.
            ext_en_output(int, optional): enable external vcsel driver signal. Defaults to None.
            ext_inv_output(int, optional): invert external vcsel driver signal. Defaults to None.
            vcsel_period(int, optional): vcsel_period in 200ps units. Defaults to None.
            vcdrv_offset(int, optional): vcdrv_offset in 200ps units. Defaults to None.
            vc_spr_spec_single_edge(int, optional):if set randomize VCDRV CP clock with each pos-edge
            vc_spr_spec_cfg(int, optional):select mode for spread spectrum
            vc_spr_spec_amp(int, optional):amplitude for spread spectrum: 0 is disable, 1..15 jitter steps in 100 us
            histogram_bins(int, optional): histogram_bins. Defaults to None.
            bin_shift(int, optional): how many bins are combined into one. Defaults to None.
            ref_bin_shift(int, optional): how many ref bins are combined into one. Defaults to None.
            tdc_offset(int, optional): tdc_offset in 200ps units. Defaults to None.
            settling(int, optional): settling in vcsel_period units. Defaults to None.
            peak_bins(int, optional):  number of bins to use for peak calculation. Defaults to None.
            ref_peak_bins(int, optional):number of bins to use for reference peak calculation. Defaults to None.
            select(int, optional): set to 1 to calculate distance, set to 0 to return bin index. Defaults to None.
            confidence_threshold(int, optional): objects which have a confidence level equal or higher will be reported . Defaults to None.
            signal_level(int, optional): detected peaks must be above this signal level (above  baseline) (0..32767)
            poisson(int, optional): poisson adjustment for noise
            peak_detect_start(int, optional): nominal start bin (for bin-shift 0 )
            min_distance_uq(int, optional):  minimum distance to report detected peaks (in quarter mm )
            parameter_a(int, optional): parameter A for tail model
            parameter_b(int, optional): parameter B for tail model
            xtalk_distance_mm(int, optional): xtalk distance in mm
            xtalk_max(int, optional): xtalk max
            xtalk_edge(int, optional): xtalk edge
            int_zone_mask(list): zone can trigger an interrupt. Defaults to None.
            int_threshold_low(int, optional): interrupt threshold for distance LSB. Defaults to None.
            int_threshold_high(int, optional): interrupt threshold for distance MSB. Defaults to None.
            int_persistence(int, optional): number of consecutive measurements that find a target inside the threshold range will trigger an interrupt. Defaults to None.
            post_processing(int, optional): 0 = persistence, 1 = motion detection. defaults to None.
            gpio0(int, optional): GPIO configuration. Defaults to None.
            gpio1(int, optional): GPIO configuration. Defaults to None.
            gpio2(int, optional): GPIO configuration. Defaults to None.
            gpio3(int, optional): GPIO configuration. Defaults to None.
            gpio4(int, optional): GPIO configuration. Defaults to None.
            gpio5(int, optional): GPIO configuration. Defaults to None.
            gpio6(int, optional): GPIO configuration. Defaults to None.
            pre_delay(int, optional): Delay for for GPIO configuration. Defaults to None.
            cpu_sleep(int,optional): CPU go to sleep as often as possible. Defaults to None.
            device_sleep(int,optional): goto standby timed if time allows. Defaults to None.
            lp_osc_device_sleep(int,optional): use low-power oscillator in standby timed. Defaults to None.
            spad_cropping(int,optional): disable unused SPAD in case the MP is disabled. Defaults to None
            spr_spec_single_edge(int,optional): spread spectrum edge modes (1=single clk edge, 0=both clk edges). Defaults to None.
            spr_spec_cfg(int,optional): spread spectrum randomization mode. Defaults to None.
            spr_spec_amp(int,optional): spread spectrum amplitude. Defaults to None.
            add_100_mm_offset(int,optional): calibration offset. Defaults to None.
            mp_top_x(int,optional): x index of top-left MP.This defines the upper left corner for MP selection. Normally it is set to 0. Defaults to None.
            mp_top_y(int,optional): y index of top-left MP.This defines the upper left corner for MP selection. Normally it is set to 0. . Defaults to None.
            mp_bottom_x(int,optional): x index of bottom-right MP.This defines the lower right corner for MP selection. Normally it is set to 15. Defaults to None.
            mp_bottom_y(int,optional):  y index of bottom-right MP.This defines the lower right corner for MP selection. Normally it is set to 15. Defaults to None.
            ref_mp(int,optional): 4bit bit-field, if set this reference MP is used for zero-offset calculation. Defaults to None.
            motion_distance(int,optional): 16bit distance difference in UQ2 (quater-mm). defaults to None.
            detect_snr(int,optional): 8 bit detection SNR must be equal or greater than this. defaults to None.
            release_snr(int,optional):8 bit release SNR must be equal or greater than this. defaults to None.
            motion_adjacent(int,optional):number of adjacent pixel that must have motion to report it. defaults to None.
            dual_mode(int,optional): set to 1 to automatically do dual integration, defaults to None.
            high_accuracy_iterations(int,optional): 16-bit unsigned integer, short range kilo iterations, defaults to None.
            prox_distance(int,optional): 8-bit unsigned integer, proximity detection distance in mm, defaults to None
            """
        self.sendCommand( Tmf8829AppRegs.TMF8829_CMD_STAT._cmd_stat._CMD_LOAD_CONFIG_PAGE )
        if (period != None):
            self.hal.tx( Tmf8829ConfigRegs.TMF8829_CFG_PERIOD_MS_LSB.addr, [period%256, period//256] )
        if (iterations != None):
            self.hal.tx( Tmf8829ConfigRegs.TMF8829_CFG_KILO_ITERATIONS_LSB.addr, [iterations%256, iterations//256] )
        if (fp_mode != None):
            self.hal.tx( Tmf8829ConfigRegs.TMF8829_CFG_FP_MODE.addr, fp_mode )
            self.cfg_fpMode = fp_mode
        if (spad_select != None):
            self.hal.tx( Tmf8829ConfigRegs.TMF8829_CFG_SPAD_SELECT.addr, spad_select )
        if (ref_spad_select != None):
            self.hal.tx( Tmf8829ConfigRegs.TMF8829_CFG_REF_SPAD_SELECT.addr, ref_spad_select )
        if (dead_time != None):
            self.hal.tx( Tmf8829ConfigRegs.TMF8829_CFG_SPAD_DEADTIME.addr, dead_time )
        if (nr_peaks != None) or (signal_strength != None) or (noise_strength != None) or (xtalk != None) or (full_noise != None):
            _resultFormat = list(self.hal.txRx([Tmf8829ConfigRegs.TMF8829_CFG_RESULT_FORMAT.addr],1))
            if (nr_peaks != None):
                _resultFormat[0] = _resultFormat[0] & ~Tmf8829ConfigRegs.TMF8829_CFG_RESULT_FORMAT._nr_peaks.mask
                _resultFormat[0] += nr_peaks & Tmf8829ConfigRegs.TMF8829_CFG_RESULT_FORMAT._nr_peaks.mask
            if (signal_strength != None):
                _resultFormat[0] = _resultFormat[0] & ~Tmf8829ConfigRegs.TMF8829_CFG_RESULT_FORMAT._signal_strength.mask
                _resultFormat[0] += (signal_strength << Tmf8829ConfigRegs.TMF8829_CFG_RESULT_FORMAT._signal_strength.shift) & Tmf8829ConfigRegs.TMF8829_CFG_RESULT_FORMAT._signal_strength.mask
            if (noise_strength != None):
                _resultFormat[0] = _resultFormat[0] & ~Tmf8829ConfigRegs.TMF8829_CFG_RESULT_FORMAT._noise_strength.mask
                _resultFormat[0] += (noise_strength << Tmf8829ConfigRegs.TMF8829_CFG_RESULT_FORMAT._noise_strength.shift) & Tmf8829ConfigRegs.TMF8829_CFG_RESULT_FORMAT._noise_strength.mask
            if (xtalk != None):
                _resultFormat[0] = _resultFormat[0] & ~Tmf8829ConfigRegs.TMF8829_CFG_RESULT_FORMAT._xtalk.mask
                _resultFormat[0] += (xtalk << Tmf8829ConfigRegs.TMF8829_CFG_RESULT_FORMAT._xtalk.shift) & Tmf8829ConfigRegs.TMF8829_CFG_RESULT_FORMAT._xtalk.mask
            if (full_noise != None):
                _resultFormat[0] = _resultFormat[0] & ~Tmf8829ConfigRegs.TMF8829_CFG_RESULT_FORMAT._full_noise.mask
                _resultFormat[0] += (full_noise << Tmf8829ConfigRegs.TMF8829_CFG_RESULT_FORMAT._full_noise.shift) & Tmf8829ConfigRegs.TMF8829_CFG_RESULT_FORMAT._full_noise.mask
            self.hal.tx( Tmf8829ConfigRegs.TMF8829_CFG_RESULT_FORMAT.addr, _resultFormat[0] )
            self.cfg_resultFormat = _resultFormat[0]
        if (histograms != None):
            self.hal.tx( Tmf8829ConfigRegs.TMF8829_CFG_DUMP_HISTOGRAMS.addr, histograms )
            self.cfg_histograms = histograms
        if (publish != None):
            self.hal.tx( Tmf8829ConfigRegs.TMF8829_CFG_REF_SPAD_FRAME.addr, publish )
            self.cfg_refFrame = publish
        if (bdv_temp_sensor != None):
            self.hal.tx( Tmf8829ConfigRegs.TMF8829_CFG_TEMP_SENSOR.addr, bdv_temp_sensor )
        if (t0_vcsel != None) or (t1_vcsel != None):
            _vcselFormat = list(self.hal.txRx([Tmf8829ConfigRegs.TMF8829_CFG_VCSEL_ON.addr],1))
            if (t0_vcsel != None):
                _vcselFormat[0] = _vcselFormat[0] & ~Tmf8829ConfigRegs.TMF8829_CFG_VCSEL_ON._t0_vcsel.mask
                _vcselFormat[0] += t0_vcsel & Tmf8829ConfigRegs.TMF8829_CFG_VCSEL_ON._t0_vcsel.mask
            if (t1_vcsel != None):
                _vcselFormat[0] = _vcselFormat[0] & ~Tmf8829ConfigRegs.TMF8829_CFG_VCSEL_ON._t1_vcsel.mask
                _vcselFormat[0] += (t1_vcsel << Tmf8829ConfigRegs.TMF8829_CFG_VCSEL_ON._t1_vcsel.shift) & Tmf8829ConfigRegs.TMF8829_CFG_VCSEL_ON._t1_vcsel.mask
            self.hal.tx( Tmf8829ConfigRegs.TMF8829_CFG_VCSEL_ON.addr, _vcselFormat[0] )
        if (dither_increment != None) or (dither_rounds != None):
            _ditherFormat = list(self.hal.txRx([Tmf8829ConfigRegs.TMF8829_CFG_DITHER.addr],1))
            if (dither_increment != None):
                _ditherFormat[0] = _ditherFormat[0] & ~Tmf8829ConfigRegs.TMF8829_CFG_DITHER._dither_increment.mask
                _ditherFormat[0] += dither_increment & Tmf8829ConfigRegs.TMF8829_CFG_DITHER._dither_increment.mask
            if (dither_rounds != None):
                _ditherFormat[0] = _ditherFormat[0] & ~Tmf8829ConfigRegs.TMF8829_CFG_DITHER._dither_rounds.mask
                _ditherFormat[0] += (dither_rounds << Tmf8829ConfigRegs.TMF8829_CFG_DITHER._dither_rounds.shift ) & Tmf8829ConfigRegs.TMF8829_CFG_DITHER._dither_rounds.mask
            self.hal.tx( Tmf8829ConfigRegs.TMF8829_CFG_DITHER.addr, _ditherFormat[0] )
        if (pulse_width != None) or (ext_clk_input != None):
            _vcdrvFormat = list(self.hal.txRx([Tmf8829ConfigRegs.TMF8829_CFG_VCDRV.addr],1))
            if (pulse_width != None):
                _vcdrvFormat[0] = _vcdrvFormat[0] & ~Tmf8829ConfigRegs.TMF8829_CFG_VCDRV._pulse_width.mask
                _vcdrvFormat[0] += pulse_width & Tmf8829ConfigRegs.TMF8829_CFG_VCDRV._pulse_width.mask
            if (ext_clk_input != None):
                _vcdrvFormat[0] = _vcdrvFormat[0] & ~Tmf8829ConfigRegs.TMF8829_CFG_VCDRV._ext_clk_input.mask
                _vcdrvFormat[0] += (ext_clk_input << Tmf8829ConfigRegs.TMF8829_CFG_VCDRV._ext_clk_input.shift) & Tmf8829ConfigRegs.TMF8829_CFG_VCDRV._ext_clk_input.mask
            self.hal.tx( Tmf8829ConfigRegs.TMF8829_CFG_VCDRV.addr, _vcdrvFormat[0] )
        if (current != None):
            self.hal.tx( Tmf8829ConfigRegs.TMF8829_CFG_VCDRV_2.addr, current )
        if (hi_len != None) or (ext_en_output != None) or (ext_inv_output != None):
            _vcdrv3Format = list(self.hal.txRx([Tmf8829ConfigRegs.TMF8829_CFG_VCDRV_3.addr],1))
            if (hi_len != None):
                _vcdrv3Format[0] = _vcdrv3Format[0] & ~Tmf8829ConfigRegs.TMF8829_CFG_VCDRV_3._hi_len.mask
                _vcdrv3Format[0] += hi_len & Tmf8829ConfigRegs.TMF8829_CFG_VCDRV_3._hi_len.mask
            if (ext_en_output != None):
                _vcdrv3Format[0] = _vcdrv3Format[0] & ~Tmf8829ConfigRegs.TMF8829_CFG_VCDRV_3._ext_en_output.mask
                _vcdrv3Format[0] += (ext_en_output << Tmf8829ConfigRegs.TMF8829_CFG_VCDRV_3._ext_en_output.shift) & Tmf8829ConfigRegs.TMF8829_CFG_VCDRV_3._ext_en_output.mask
            if (ext_inv_output != None):
                _vcdrv3Format[0] = _vcdrv3Format[0] & ~Tmf8829ConfigRegs.TMF8829_CFG_VCDRV_3._ext_inv_output.mask
                _vcdrv3Format[0] += (ext_inv_output << Tmf8829ConfigRegs.TMF8829_CFG_VCDRV_3._ext_inv_output.shift) & Tmf8829ConfigRegs.TMF8829_CFG_VCDRV_3._ext_inv_output.mask
            self.hal.tx( Tmf8829ConfigRegs.TMF8829_CFG_VCDRV_3.addr, _vcdrv3Format[0] )
        if (vcsel_period != None):
            self.hal.tx( Tmf8829ConfigRegs.TMF8829_VCSEL_PERIOD_200PS_LSB.addr, [vcsel_period%256, vcsel_period//256] )
        if (vcdrv_offset != None):
            self.hal.tx( Tmf8829ConfigRegs.TMF8829_VCDRV_OFFSET_200PS_LSB.addr, [vcdrv_offset%256, vcdrv_offset//256] )
        _vc_spr_spec = self.hal.txRx( Tmf8829ConfigRegs.TMF8829_VCDRV_CP.addr,1)[0]
        _orig_vc_spr_spec = _vc_spr_spec
        if vc_spr_spec_single_edge != None:
            _vc_spr_spec = _vc_spr_spec & ~Tmf8829ConfigRegs.TMF8829_VCDRV_CP._vc_spr_spec_single_edge.mask
            _vc_spr_spec += ( vc_spr_spec_single_edge << Tmf8829ConfigRegs.TMF8829_VCDRV_CP._vc_spr_spec_single_edge.shift) & Tmf8829ConfigRegs.TMF8829_VCDRV_CP._vc_spr_spec_single_edge.mask
        if vc_spr_spec_cfg != None:
            _vc_spr_spec = _vc_spr_spec & ~Tmf8829ConfigRegs.TMF8829_VCDRV_CP._vc_spr_spec_cfg.mask
            _vc_spr_spec += ( vc_spr_spec_cfg << Tmf8829ConfigRegs.TMF8829_VCDRV_CP._vc_spr_spec_cfg.shift) & Tmf8829ConfigRegs.TMF8829_VCDRV_CP._vc_spr_spec_cfg.mask
        if vc_spr_spec_amp != None:
            _vc_spr_spec = _vc_spr_spec & ~Tmf8829ConfigRegs.TMF8829_VCDRV_CP._vc_spr_spec_amp.mask
            _vc_spr_spec += ( vc_spr_spec_amp << Tmf8829ConfigRegs.TMF8829_VCDRV_CP._vc_spr_spec_amp.shift) & Tmf8829ConfigRegs.TMF8829_VCDRV_CP._vc_spr_spec_amp.mask
        if _orig_vc_spr_spec != _vc_spr_spec:
            self.hal.tx( Tmf8829ConfigRegs.TMF8829_VCDRV_CP.addr, _vc_spr_spec )
        # TDC configuration
        if (histogram_bins != None):
            self.hal.tx( Tmf8829ConfigRegs.TMF8829_HISTOGRAM_BINS_LSB.addr, [ histogram_bins%256, histogram_bins//256] )          
        if (bin_shift != None):
            self.hal.tx( Tmf8829ConfigRegs.TMF8829_BIN_SHIFT.addr, bin_shift )
        if (ref_bin_shift != None):
            self.hal.tx( Tmf8829ConfigRegs.TMF8829_REF_BIN_SHIFT.addr, ref_bin_shift )
        if (tdc_offset != None):
            self.hal.tx( Tmf8829ConfigRegs.TMF8829_TDC_OFFSET_200PS_LSB.addr, [tdc_offset%256, tdc_offset//256] )
        if (settling != None):
            self.hal.tx( Tmf8829ConfigRegs.TMF8829_TDC_PRE_PERIODS_LSB.addr, [settling%256, settling//256] )
        # Algorithm configuration
        if (peak_bins != None):
            self.hal.tx( Tmf8829ConfigRegs.TMF8829_CFG_ALG_PEAK_BINS.addr, peak_bins)
        if (ref_peak_bins != None):
            self.hal.tx( Tmf8829ConfigRegs.TMF8829_CFG_ALG_REF_PEAK_BINS.addr, ref_peak_bins )  
        if (select != None):
            self.hal.tx( Tmf8829ConfigRegs.TMF8829_CFG_ALG_DISTANCE.addr, select )     
        if (confidence_threshold != None):
            self.hal.tx( Tmf8829ConfigRegs.TMF8829_CFG_ALG_CONFIDENCE_THRESHOLD.addr, confidence_threshold )
        if (signal_level != None):
            self.hal.tx( Tmf8829ConfigRegs.TMF8829_CFG_ALG_MIN_SIGNAL_LEVEL_LSB.addr, [signal_level%256, signal_level//256] )
        if (poisson != None):
            self.hal.tx( Tmf8829ConfigRegs.TMF8829_CFG_ALG_POISSONADJUST.addr, poisson )
        if (peak_detect_start != None):
            self.hal.tx( Tmf8829ConfigRegs.TMF8829_CFG_ALG_HW_PEAK_START.addr, peak_detect_start )
        if (min_distance_uq != None):
            self.hal.tx( Tmf8829ConfigRegs.TMF8829_CFG_ALG_MIN_DISTANCE_LSB.addr, [min_distance_uq%256, min_distance_uq//256] )
        if (parameter_a != None):
            self.hal.tx( Tmf8829ConfigRegs.TMF8829_CFG_ALG_TAIL_MODEL_A_LSB.addr, [parameter_a%256, parameter_a//256] )
        if (parameter_b != None):
            self.hal.tx( Tmf8829ConfigRegs.TMF8829_CFG_ALG_TAIL_MODEL_B_LSB.addr, [parameter_b%256, parameter_b//256] )
        if (xtalk_distance_mm != None ):
            self.hal.tx( Tmf8829ConfigRegs.TMF8829_CFG_ALG_XTALK_DISTANCE_MM.addr, [xtalk_distance_mm] )
        if (xtalk_max != None):
            self.hal.tx( Tmf8829ConfigRegs.TMF8829_CFG_ALG_XTALK_MAX_LSB.addr, [xtalk_max%256, xtalk_max//256] )
        if (xtalk_edge != None):
            self.hal.tx( Tmf8829ConfigRegs.TMF8829_CFG_ALG_XTALK_EDGE_LSB.addr, [xtalk_edge%256, xtalk_edge//256] )
        if (int_zone_mask != None):
            self.hal.tx( Tmf8829ConfigRegs.TMF8829_CFG_INT_ZONE_MASK_0.addr , int_zone_mask )
        if (int_threshold_low != None):
            self.hal.tx( Tmf8829ConfigRegs.TMF8829_CFG_INT_THRESHOLD_LOW_LSB.addr, [int_threshold_low%256, int_threshold_low//256] )
        if (int_threshold_high != None):
            self.hal.tx( Tmf8829ConfigRegs.TMF8829_CFG_INT_THRESHOLD_HIGH_LSB.addr, [int_threshold_high%256, int_threshold_high//256] )
        if (int_persistence != None):
            self.hal.tx( Tmf8829ConfigRegs.TMF8829_CFG_INT_PERSISTENCE.addr, int_persistence )
        if (post_processing != None):
            self.hal.tx( Tmf8829ConfigRegs.TMF8829_CFG_POST_PROCESSING.addr, post_processing )
        if (add_100_mm_offset != None):
            self.hal.tx( Tmf8829ConfigRegs.TMF8829_CFG_ALG_CALIBRATION.addr, add_100_mm_offset)
        if ( mp_top_x != None ):
            self.hal.tx( Tmf8829ConfigRegs.TMF8829_CFG_CROP_TOP_X.addr, mp_top_x )
        if ( mp_top_y != None ):
            self.hal.tx( Tmf8829ConfigRegs.TMF8829_CFG_CROP_TOP_Y.addr, mp_top_y )
        if ( mp_bottom_x != None ):
            self.hal.tx( Tmf8829ConfigRegs.TMF8829_CFG_CROP_BOTTOM_X.addr, mp_bottom_x )
        if ( mp_bottom_y != None ):
            self.hal.tx( Tmf8829ConfigRegs.TMF8829_CFG_CROP_BOTTOM_Y.addr, mp_bottom_y )
        if ( ref_mp != None ):
            self.hal.tx( Tmf8829ConfigRegs.TMF8829_CFG_CROP_REFERENCE.addr, ref_mp )
        if (gpio0 != None):
            self.hal.tx( Tmf8829ConfigRegs.TMF8829_CFG_GPIO_0.addr, gpio0 )
        if (gpio1 != None):
            self.hal.tx( Tmf8829ConfigRegs.TMF8829_CFG_GPIO_1.addr, gpio1 )
        if (gpio2 != None):
            self.hal.tx( Tmf8829ConfigRegs.TMF8829_CFG_GPIO_2.addr, gpio2 )
        if (gpio3 != None):
            self.hal.tx( Tmf8829ConfigRegs.TMF8829_CFG_GPIO_3.addr, gpio3 )
        if (gpio4 != None):
            self.hal.tx( Tmf8829ConfigRegs.TMF8829_CFG_GPIO_4.addr, gpio4 )
        if (gpio5 != None):
            self.hal.tx( Tmf8829ConfigRegs.TMF8829_CFG_GPIO_5.addr, gpio5 )
        if (gpio6 != None):
            self.hal.tx( Tmf8829ConfigRegs.TMF8829_CFG_GPIO_6.addr, gpio6 )
        if (pre_delay != None):
            self.hal.tx( Tmf8829ConfigRegs.TMF8829_CFG_GPIO.addr, pre_delay )
        _power_mode = self.hal.txRx( Tmf8829ConfigRegs.TMF8829_CFG_POWER_MODES.addr, 1 )[0]
        self.cfg_powerMode = _power_mode
        if cpu_sleep != None:
            _power_mode = _power_mode & ~Tmf8829ConfigRegs.TMF8829_CFG_POWER_MODES._cpu_sleep.mask
            _power_mode += ( cpu_sleep << Tmf8829ConfigRegs.TMF8829_CFG_POWER_MODES._cpu_sleep.shift) & Tmf8829ConfigRegs.TMF8829_CFG_POWER_MODES._cpu_sleep.mask
        if device_sleep != None:
            _power_mode = _power_mode & ~Tmf8829ConfigRegs.TMF8829_CFG_POWER_MODES._device_sleep.mask
            _power_mode += ( device_sleep << Tmf8829ConfigRegs.TMF8829_CFG_POWER_MODES._device_sleep.shift) & Tmf8829ConfigRegs.TMF8829_CFG_POWER_MODES._device_sleep.mask
        if lp_osc_device_sleep != None:
            _power_mode = _power_mode & ~Tmf8829ConfigRegs.TMF8829_CFG_POWER_MODES._lp_osc_device_sleep.mask
            _power_mode += ( lp_osc_device_sleep << Tmf8829ConfigRegs.TMF8829_CFG_POWER_MODES._lp_osc_device_sleep.shift) & Tmf8829ConfigRegs.TMF8829_CFG_POWER_MODES._lp_osc_device_sleep.mask
        if spad_cropping != None:
            _power_mode = _power_mode & ~Tmf8829ConfigRegs.TMF8829_CFG_POWER_MODES._spad_cropping.mask
            _power_mode += ( spad_cropping << Tmf8829ConfigRegs.TMF8829_CFG_POWER_MODES._spad_cropping.shift) & Tmf8829ConfigRegs.TMF8829_CFG_POWER_MODES._spad_cropping.mask
        if self.cfg_powerMode != _power_mode:
            self.hal.tx( Tmf8829ConfigRegs.TMF8829_CFG_POWER_MODES.addr, _power_mode )
            self.cfg_powerMode = _power_mode
        _spr_spec = self.hal.txRx( Tmf8829ConfigRegs.TMF8829_HV_CP.addr,1)[0]
        _orig_spr_spec = _spr_spec
        if spr_spec_single_edge != None:
            _spr_spec = _spr_spec & ~Tmf8829ConfigRegs.TMF8829_HV_CP._spr_spec_single_edge.mask
            _spr_spec += ( spr_spec_single_edge << Tmf8829ConfigRegs.TMF8829_HV_CP._spr_spec_single_edge.shift) & Tmf8829ConfigRegs.TMF8829_HV_CP._spr_spec_single_edge.mask
        if spr_spec_cfg != None:
            _spr_spec = _spr_spec & ~Tmf8829ConfigRegs.TMF8829_HV_CP._spr_spec_cfg.mask
            _spr_spec += ( spr_spec_cfg << Tmf8829ConfigRegs.TMF8829_HV_CP._spr_spec_cfg.shift) & Tmf8829ConfigRegs.TMF8829_HV_CP._spr_spec_cfg.mask
        if spr_spec_amp != None:
            _spr_spec = _spr_spec & ~Tmf8829ConfigRegs.TMF8829_HV_CP._spr_spec_amp.mask
            _spr_spec += ( spr_spec_amp << Tmf8829ConfigRegs.TMF8829_HV_CP._spr_spec_amp.shift) & Tmf8829ConfigRegs.TMF8829_HV_CP._spr_spec_amp.mask
        if _orig_spr_spec != _spr_spec:
            self.hal.tx( Tmf8829ConfigRegs.TMF8829_HV_CP.addr, _spr_spec )
        if (motion_distance != None):
            self.hal.tx( Tmf8829ConfigRegs.TMF8829_CFG_MOTION_DETECT_DISTANCE_LSB.addr, [motion_distance%256, motion_distance//256] )
        if (detect_snr != None):
            self.hal.tx( Tmf8829ConfigRegs.TMF8829_CFG_MOTION_DETECT_SNR .addr, detect_snr )
        if (release_snr != None):
            self.hal.tx( Tmf8829ConfigRegs.TMF8829_CFG_MOTION_RELEASE_SNR .addr, release_snr )
        if (motion_adjacent != None):
            self.hal.tx( Tmf8829ConfigRegs.TMF8829_CFG_MOTION_ADJACENT_PIXEL.addr, motion_adjacent )
        if (high_accuracy_iterations != None):
            self.hal.tx( Tmf8829ConfigRegs.TMF8829_CFG_HA_KILO_ITERATIONS_LSB.addr, [high_accuracy_iterations%256, high_accuracy_iterations//256] )
        if (dual_mode != None):
            self.hal.tx( Tmf8829ConfigRegs.TMF8829_CFG_ENABLE_DUAL_MODE.addr, dual_mode )
            self.cfg_dualMode = dual_mode
        if (prox_distance != None):
            self.hal.tx( Tmf8829ConfigRegs.TMF8829_CFG_PROX_DISTANCE.addr, prox_distance )

        self.sendCommand( Tmf8829AppRegs.TMF8829_CMD_STAT._cmd_stat._CMD_WRITE_PAGE )

    def loadConfig(self) -> bytearray:
        """Read the I2C configuration page from the device.

        Returns:
            bytearray: Bytearray of read registers.
        """
        self.sendCommand( Tmf8829AppRegs.TMF8829_CMD_STAT._cmd_stat._CMD_LOAD_CONFIG_PAGE ) # load the config page.
        number_regs =  Tmf8829ConfigRegs.TMF8829_CFG_LAST_AVAILABLE.addr - Tmf8829ConfigRegs.TMF8829_CFG_PERIOD_MS_LSB.addr + 1 # whole until HW regs start
        val = self.hal.txRx([Tmf8829ConfigRegs.TMF8829_CFG_PERIOD_MS_LSB.addr], number_regs)  # Now read the data via I2C.

        self.cfg_fpMode = (val[Tmf8829ConfigRegs.TMF8829_CFG_FP_MODE.addr-Tmf8829ConfigRegs.TMF8829_CFG_PERIOD_MS_LSB.addr]
                          & Tmf8829ConfigRegs.TMF8829_CFG_FP_MODE._fp_mode.mask) >> Tmf8829ConfigRegs.TMF8829_CFG_FP_MODE._fp_mode.shift
        self.cfg_resultFormat = val[Tmf8829ConfigRegs.TMF8829_CFG_RESULT_FORMAT.addr - Tmf8829ConfigRegs.TMF8829_CFG_PERIOD_MS_LSB.addr]
        self.cfg_histograms = (val[Tmf8829ConfigRegs.TMF8829_CFG_DUMP_HISTOGRAMS.addr-Tmf8829ConfigRegs.TMF8829_CFG_PERIOD_MS_LSB.addr] \
                              & Tmf8829ConfigRegs.TMF8829_CFG_DUMP_HISTOGRAMS._histograms.mask) >> Tmf8829ConfigRegs.TMF8829_CFG_DUMP_HISTOGRAMS._histograms.shift
        self.cfg_refFrame = (val[Tmf8829ConfigRegs.TMF8829_CFG_REF_SPAD_FRAME.addr-Tmf8829ConfigRegs.TMF8829_CFG_PERIOD_MS_LSB.addr]
                            & Tmf8829ConfigRegs.TMF8829_CFG_REF_SPAD_FRAME._publish.mask) >> Tmf8829ConfigRegs.TMF8829_CFG_REF_SPAD_FRAME._publish.shift
        self.cfg_dualMode = (val[Tmf8829ConfigRegs.TMF8829_CFG_ENABLE_DUAL_MODE.addr-Tmf8829ConfigRegs.TMF8829_CFG_PERIOD_MS_LSB.addr]
                            & Tmf8829ConfigRegs.TMF8829_CFG_ENABLE_DUAL_MODE._dual_mode.mask) >> Tmf8829ConfigRegs.TMF8829_CFG_ENABLE_DUAL_MODE._dual_mode.shift
        return val

    def readApplicationRegisters(self) -> bytes:
        """Function to read the Application Registers.
        Return:
            Dictionary of the calibration data
        """
        _number_regs = Tmf8829AppRegs.TMF8829_PAYLOAD.addr - Tmf8829AppRegs.TMF8829_APP_ID.addr + 1 
        _data = self.hal.txRx([Tmf8829AppRegs.TMF8829_APP_ID.addr], _number_regs )
        
        return RegisterPageConverter.readPageToDict( _data,Tmf8829AppRegs())

    def readFrameWithSize(self,_data_size):
        """Function reads a frame size based.
        Args:
            _data_size: data size without header and footer
        Returns:
            list[int]: frame content + preheader as byte list
        """
        _header_size = ctypes.sizeof(struct__tmf8829FrameHeader)
        _footer_size = ctypes.sizeof(struct__tmf8829FrameFooter)
        _frame = self.hal.txRx([Tmf8829HostRegs.FIFOSTATUS.addr],self.PRE_HEADER_SIZE+_header_size+_data_size+_footer_size)
        _footer = tmf8829FrameFooter.from_buffer_copy( _frame[-_footer_size:])  # get the last _footer_size bytes as footer
        if _footer.eof != TMF8829_FRAME_EOF:
            assert _footer.eof == TMF8829_FRAME_EOF, "Error frame has no EOF marker but {}".format(_footer.eof )
        if _footer.frameStatus & TMF8829_FRAME_WARNING_HV_CP_OVERLOAD:
            print( "WARNING FRAME has TMF8829_FRAME_WARNING_HV_CP_OVERLOAD flagged") 
        if _footer.frameStatus & TMF8829_FRAME_WARNING_VCDRV_OVERLOAD:
            print( "WARNING FRAME has TMF8829_FRAME_WARNING_VCDRV_OVERLOAD flagged") 
        if _footer.frameStatus & TMF8829_FRAME_WARNING_VCDRV_BURST_EXCEEDED:
            print( "WARNING FRAME has TMF8829_FRAME_WARNING_VCDRV_BURST_EXCEEDED flagged") 

        assert (_footer.frameStatus & TMF8829_FRAME_VALID), "Error frame status is not valid but {}".format(_footer.frameStatus )
        _data = list(_frame)

        return _data

    def readFrames(self,interrupt):
        """Function reads a single frames from a fifo and returns them in the first item of a tuple as multi-dimentional array.
           The second item hold an reference result frame if publish mode is on and the read Frame is an result frame.

        Args:
            interrupt (int): interrupt value
        Returns:
            tuple:  first item: preheader + frame content + footer as byte list
                   second item: preheader + result frame content if available, otherwise None
           """
        if interrupt == TMF8829_INT_HISTOGRAMS:
            _frame = self.readFrameWithSize( Tmf8829AppCommon.histogramFrameDataSize(self.cfg_fpMode) )
        elif interrupt == TMF8829_INT_RESULTS:
            if self.cfg_refFrame:
                _refFrame = self.readRefSpadFrameIfAvailable()
            _frame = self.readFrameWithSize( Tmf8829AppCommon.resultFrameDataSize(self.cfg_fpMode,self.cfg_resultFormat))
            if self.cfg_refFrame:
                return (_frame, _refFrame)
        else:
            print( "Interrupts={}".format(hex(interrupt)))
            raise RuntimeError( "Cannot have 2 interrupts at same time, not clear which frame to read ")
        return (_frame, None)

    def readFramesAndWait(self, timeout:float=5.0, useIntPin=False):
        """Function reads a single frames from a fifo and returns them in the first item of a tuple as multi-dimentional array.
           The second item hold an reference result frame if publish mode is on and the read Frame is an result frame.
        Args:
            timeout (float, optional): Max time for timeout. Defaults to 5.0.
            useIntPin (bool, optional): Set True for using the interrupt pin, otherwise the interrupt register is polled. Defaults to False.
        Returns:
            tuple:  first item: preheader + frame content + footer as byte list, otherwise None
                   second item: preheader + result frame content if available, otherwise None
        """
        _max_time = time.time() + timeout
        while True:
            if ( (not useIntPin) or ((useIntPin) and self.isIntPinPulledLow())):
                if self.isDeviceWakeup():                                               # only access device while it is not in standby/standby-timed
                    status = self.readAndClearInt( TMF8829_INT_HISTOGRAMS | TMF8829_INT_RESULTS )
                    if status:
                        return self.readFrames(status)
            if time.time() > _max_time:
                raise Exception( "Error timeout timeout={}, max_time={}".format(timeout, _max_time ))

    def readFramesIfAvailable(self, useIntPin=False, log=False):
        """Function reads a single frames from a fifo and returns them in the first item of a tuple as multi-dimensional array.
        If no frame is available returns None
        The second item hold an reference result frame if publish mode is on and the read Frame is an result frame.

        Args:
            useIntPin (bool, optional): interrupt value. Defaults to False.
            log (bool,optional): prints that device is in Standby/Standby-timed if set to True in case device is in low-power mode

        Returns:
            tuple:  first item: preheader + frame content + footer as byte list, otherwise None
                   second item: preheader + result frame content if available, otherwise None
        """        
    
        if useIntPin:
            if not self.isIntPinPulledLow():
                return (None, None)
        if self.isDeviceWakeup():
            status = self.readAndClearInt(TMF8829_INT_HISTOGRAMS | TMF8829_INT_RESULTS)
            if status:
                return self.readFrames(status)
        elif log:
            print( "Standby/Standby-timed")
        return (None, None)

    def readRefSpadFrameIfAvailable(self):
        """Reads and returns a reference SPAD frame if available, otherwise returns None.
        Returns:
            list[int] | None : reference frame content 
        """
        data = self.hal.txRx([Tmf8829AppRegs.TMF8829_CID_RID.addr], ctypes.sizeof(tmf8829RefSpadFrame))
        frame = tmf8829RefSpadFrame.from_buffer_copy(data)
        if ( frame.header.id & TMF8829_FID_MASK ) == TMF8829_FID_REF_SPAD_SCAN:
            return [0]*self.PRE_HEADER_SIZE + list( data )  # add artificial pre-header as they are not read from FIFO
        else:
            return None

    def readMeasurementFrames(self, timeout:float=5.0, useIntPin=False):
        """The result set of a measurement.
        Args:
            timeout (float, optional): Max time for timeout. Defaults to 5.0.
            useIntPin (bool, optional): set True for using the interrupt pin, otherwise the interrupt register is polled. Defaults to False.
        Returns:
            tuple(list[bytearray],list[bytearray],list[bytearray]): returns the list of result frames,
                list of histogram frames and list of reference frames.
        """
        frames = []
        expected_frames = self.numberOfFramesPerMeasurement()
        received_frames = 0
        while received_frames < expected_frames:
            readFrames, refFrame = self.readFramesAndWait(timeout=timeout, useIntPin=useIntPin)
            frames += readFrames
            received_frames += 1
            if refFrame:                             
                frames += refFrame
                received_frames += 1

        return Tmf8829AppCommon.getFramesFromMeasurementResult(frames) # separate in result frames, histogram frames and ref frames
