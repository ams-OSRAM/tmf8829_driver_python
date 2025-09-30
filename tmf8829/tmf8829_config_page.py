# *****************************************************************************
# * Copyright by ams OSRAM AG                                                 *
# * All rights are reserved.                                                  *
# *                                                                           *
# *FOR FULL LICENSE TEXT SEE LICENSES-MIT.TXT                                 *
# *****************************************************************************
import ctypes

class Tmf8829_config_page:

	addr_width = 8
	data_width = 8

	class TMF8829_CFG_PERIOD_MS_LSB(ctypes.LittleEndianStructure):
		addr = 0x22
		_pack_ = 1
		_fields_ = [
			("period_7_0",ctypes.c_uint8,8),
			]
		class _period_7_0:
			reset = 33
			mask  = 255
			width = 8
			shift = 0
		def __init__(self):
			self.period_7_0 = self._period_7_0.reset

	class TMF8829_CFG_PERIOD_MS_MSB(ctypes.LittleEndianStructure):
		addr = 0x23
		_pack_ = 1
		_fields_ = [
			("period_15_8",ctypes.c_uint8,8),
			]
		class _period_15_8:
			reset = 0
			mask  = 255
			width = 8
			shift = 0
		def __init__(self):
			self.period_15_8 = self._period_15_8.reset

	class TMF8829_CFG_KILO_ITERATIONS_LSB(ctypes.LittleEndianStructure):
		addr = 0x24
		_pack_ = 1
		_fields_ = [
			("iterations_7_0",ctypes.c_uint8,8),
			]
		class _iterations_7_0:
			reset = 74
			mask  = 255
			width = 8
			shift = 0
		def __init__(self):
			self.iterations_7_0 = self._iterations_7_0.reset

	class TMF8829_CFG_KILO_ITERATIONS_MSB(ctypes.LittleEndianStructure):
		addr = 0x25
		_pack_ = 1
		_fields_ = [
			("iterations_15_8",ctypes.c_uint8,8),
			]
		class _iterations_15_8:
			reset = 2
			mask  = 255
			width = 8
			shift = 0
		def __init__(self):
			self.iterations_15_8 = self._iterations_15_8.reset

	class TMF8829_CFG_FP_MODE(ctypes.LittleEndianStructure):
		addr = 0x26
		_pack_ = 1
		_fields_ = [
			("fp_mode",ctypes.c_uint8,3),
			]
		class _fp_mode:
			reset = 2
			mask  = 7
			width = 3
			shift = 0
			_FP_8x8A = 0 # 8x8 digital combine
			_FP_8x8B = 1 # 8x8 analog combine, do not use
			_FP_16x16 = 2 # 16x16 1x time-multiplexed
			_FP_32x32 = 3 # 32x32 8x time-multiplexed and 2 spad are used per MP
			_FP_32x32s = 4 # 32x32 8x time-multiplexed and 1 (single) spad is used per MP
			_FP_48x32 = 5 # 48x32 12x time-multiplexed and 1 (single) spad is used per MP
		def __init__(self):
			self.fp_mode = self._fp_mode.reset

	class TMF8829_CFG_SPAD_SELECT(ctypes.LittleEndianStructure):
		addr = 0x27
		_pack_ = 1
		_fields_ = [
			("spad_select",ctypes.c_uint8,6),
			]
		class _spad_select:
			reset = 63
			mask  = 63
			width = 6
			shift = 0
		def __init__(self):
			self.spad_select = self._spad_select.reset

	class TMF8829_CFG_REF_SPAD_SELECT(ctypes.LittleEndianStructure):
		addr = 0x28
		_pack_ = 1
		_fields_ = [
			("ref_spad_select",ctypes.c_uint8,6),
			]
		class _ref_spad_select:
			reset = 2
			mask  = 63
			width = 6
			shift = 0
			_NONE = 0 # no reference spad is selected
			_LOW_ATTENUATED_TOP = 1 # low attenuated top row
			_HIGH_ATTENUATED_TOP = 2 # high attenuated top row
			_MID_ATTENUATED_TOP = 4 # mid attenuated top row
			_LOW_ATTENUATED_BOTTOM = 8 # low attenuated bottom row
			_HIGH_ATTENUATED_BOTTOM = 16 # high attenuated bottom row
			_MID_ATTENUATED_BOTTOM = 32 # mid attenuated bottom row
		def __init__(self):
			self.ref_spad_select = self._ref_spad_select.reset

	class TMF8829_CFG_SPAD_DEADTIME(ctypes.LittleEndianStructure):
		addr = 0x29
		_pack_ = 1
		_fields_ = [
			("dead_time",ctypes.c_uint8,6),
			]
		class _dead_time:
			reset = 60
			mask  = 63
			width = 6
			shift = 0
		def __init__(self):
			self.dead_time = self._dead_time.reset

	class TMF8829_CFG_RESULT_FORMAT(ctypes.LittleEndianStructure):
		addr = 0x2a
		_pack_ = 1
		_fields_ = [
			("nr_peaks",ctypes.c_uint8,3),
			("signal_strength",ctypes.c_uint8,1),
			("noise_strength",ctypes.c_uint8,1),
			("xtalk",ctypes.c_uint8,1),
			("sub_result",ctypes.c_uint8,1),
			("full_noise",ctypes.c_uint8,1),
			]
		class _nr_peaks:
			reset = 1
			mask  = 7
			width = 3
			shift = 0
		class _signal_strength:
			reset = 0
			mask  = 8
			width = 1
			shift = 3
		class _noise_strength:
			reset = 0
			mask  = 16
			width = 1
			shift = 4
		class _xtalk:
			reset = 0
			mask  = 32
			width = 1
			shift = 5
		class _sub_result:
			reset = 0
			mask  = 64
			width = 1
			shift = 6
		class _full_noise:
			reset = 0
			mask  = 128
			width = 1
			shift = 7
		def __init__(self):
			self.nr_peaks = self._nr_peaks.reset
			self.signal_strength = self._signal_strength.reset
			self.noise_strength = self._noise_strength.reset
			self.xtalk = self._xtalk.reset
			self.sub_result = self._sub_result.reset
			self.full_noise = self._full_noise.reset

	class TMF8829_CFG_DUMP_HISTOGRAMS(ctypes.LittleEndianStructure):
		addr = 0x2b
		_pack_ = 1
		_fields_ = [
			("histograms",ctypes.c_uint8,1),
			]
		class _histograms:
			reset = 0
			mask  = 1
			width = 1
			shift = 0
		def __init__(self):
			self.histograms = self._histograms.reset

	class TMF8829_CFG_REF_SPAD_FRAME(ctypes.LittleEndianStructure):
		addr = 0x2c
		_pack_ = 1
		_fields_ = [
			("publish",ctypes.c_uint8,1),
			]
		class _publish:
			reset = 0
			mask  = 1
			width = 1
			shift = 0
		def __init__(self):
			self.publish = self._publish.reset

	class TMF8829_CFG_TEMP_SENSOR(ctypes.LittleEndianStructure):
		addr = 0x2d
		_pack_ = 1
		_fields_ = [
			("bdv_temp_sensor",ctypes.c_uint8,2),
			]
		class _bdv_temp_sensor:
			reset = 1
			mask  = 3
			width = 2
			shift = 0
		def __init__(self):
			self.bdv_temp_sensor = self._bdv_temp_sensor.reset

	class TMF8829_CFG_POWER_MODES(ctypes.LittleEndianStructure):
		addr = 0x2e
		_pack_ = 1
		_fields_ = [
			("cpu_sleep",ctypes.c_uint8,1),
			("device_sleep",ctypes.c_uint8,1),
			("lp_osc_device_sleep",ctypes.c_uint8,1),
			("spad_cropping",ctypes.c_uint8,1),
			]
		class _cpu_sleep:
			reset = 1
			mask  = 1
			width = 1
			shift = 0
		class _device_sleep:
			reset = 0
			mask  = 2
			width = 1
			shift = 1
		class _lp_osc_device_sleep:
			reset = 1
			mask  = 4
			width = 1
			shift = 2
		class _spad_cropping:
			reset = 0
			mask  = 8
			width = 1
			shift = 3
		def __init__(self):
			self.cpu_sleep = self._cpu_sleep.reset
			self.device_sleep = self._device_sleep.reset
			self.lp_osc_device_sleep = self._lp_osc_device_sleep.reset
			self.spad_cropping = self._spad_cropping.reset

	class TMF8829_CFG_VCSEL_ON(ctypes.LittleEndianStructure):
		addr = 0x30
		_pack_ = 1
		_fields_ = [
			("t0_vcsel",ctypes.c_uint8,2),
			("t1_vcsel",ctypes.c_uint8,2),
			]
		class _t0_vcsel:
			reset = 2
			mask  = 3
			width = 2
			shift = 0
		class _t1_vcsel:
			reset = 1
			mask  = 12
			width = 2
			shift = 2
		def __init__(self):
			self.t0_vcsel = self._t0_vcsel.reset
			self.t1_vcsel = self._t1_vcsel.reset

	class TMF8829_CFG_DITHER(ctypes.LittleEndianStructure):
		addr = 0x31
		_pack_ = 1
		_fields_ = [
			("dither_increment",ctypes.c_uint8,3),
			("TMF8829_CFG_DITHER_resv_3",ctypes.c_uint8,1),
			("dither_rounds",ctypes.c_uint8,3),
			]
		class _dither_increment:
			reset = 0
			mask  = 7
			width = 3
			shift = 0
		class _TMF8829_CFG_DITHER_resv_3:
			reset = 0
			mask  = 0
			width = 0
			shift = 0
		class _dither_rounds:
			reset = 0
			mask  = 112
			width = 3
			shift = 4
		def __init__(self):
			self.dither_increment = self._dither_increment.reset
			self.TMF8829_CFG_DITHER_resv_3 = self._TMF8829_CFG_DITHER_resv_3.reset
			self.dither_rounds = self._dither_rounds.reset

	class TMF8829_CFG_VCDRV(ctypes.LittleEndianStructure):
		addr = 0x32
		_pack_ = 1
		_fields_ = [
			("pulse_width",ctypes.c_uint8,2),
			("TMF8829_CFG_VCDRV_resv_2",ctypes.c_uint8,5),
			("ext_clk_input",ctypes.c_uint8,1),
			]
		class _pulse_width:
			reset = 3
			mask  = 3
			width = 2
			shift = 0
		class _TMF8829_CFG_VCDRV_resv_2:
			reset = 0
			mask  = 0
			width = 0
			shift = 0
		class _ext_clk_input:
			reset = 0
			mask  = 128
			width = 1
			shift = 7
		def __init__(self):
			self.pulse_width = self._pulse_width.reset
			self.TMF8829_CFG_VCDRV_resv_2 = self._TMF8829_CFG_VCDRV_resv_2.reset
			self.ext_clk_input = self._ext_clk_input.reset

	class TMF8829_CFG_VCDRV_2(ctypes.LittleEndianStructure):
		addr = 0x33
		_pack_ = 1
		_fields_ = [
			("current",ctypes.c_uint8,7),
			]
		class _current:
			reset = 93
			mask  = 127
			width = 7
			shift = 0
		def __init__(self):
			self.current = self._current.reset

	class TMF8829_CFG_VCDRV_3(ctypes.LittleEndianStructure):
		addr = 0x34
		_pack_ = 1
		_fields_ = [
			("hi_len",ctypes.c_uint8,4),
			("ext_en_output",ctypes.c_uint8,1),
			("ext_inv_output",ctypes.c_uint8,1),
			]
		class _hi_len:
			reset = 0
			mask  = 15
			width = 4
			shift = 0
		class _ext_en_output:
			reset = 0
			mask  = 16
			width = 1
			shift = 4
		class _ext_inv_output:
			reset = 0
			mask  = 32
			width = 1
			shift = 5
		def __init__(self):
			self.hi_len = self._hi_len.reset
			self.ext_en_output = self._ext_en_output.reset
			self.ext_inv_output = self._ext_inv_output.reset

	class TMF8829_VCSEL_PERIOD_200PS_LSB(ctypes.LittleEndianStructure):
		addr = 0x36
		_pack_ = 1
		_fields_ = [
			("vcsel_period_7_0",ctypes.c_uint8,8),
			]
		class _vcsel_period_7_0:
			reset = 249
			mask  = 255
			width = 8
			shift = 0
		def __init__(self):
			self.vcsel_period_7_0 = self._vcsel_period_7_0.reset

	class TMF8829_VCSEL_PERIOD_200PS_MSB(ctypes.LittleEndianStructure):
		addr = 0x37
		_pack_ = 1
		_fields_ = [
			("vcsel_period_9_8",ctypes.c_uint8,2),
			]
		class _vcsel_period_9_8:
			reset = 0
			mask  = 3
			width = 2
			shift = 0
		def __init__(self):
			self.vcsel_period_9_8 = self._vcsel_period_9_8.reset

	class TMF8829_VCDRV_OFFSET_200PS_LSB(ctypes.LittleEndianStructure):
		addr = 0x38
		_pack_ = 1
		_fields_ = [
			("vcdrv_offset_7_0",ctypes.c_uint8,8),
			]
		class _vcdrv_offset_7_0:
			reset = 0
			mask  = 255
			width = 8
			shift = 0
		def __init__(self):
			self.vcdrv_offset_7_0 = self._vcdrv_offset_7_0.reset

	class TMF8829_VCDRV_OFFSET_200PS_MSB(ctypes.LittleEndianStructure):
		addr = 0x39
		_pack_ = 1
		_fields_ = [
			("vcdrv_offset_9_8",ctypes.c_uint8,2),
			]
		class _vcdrv_offset_9_8:
			reset = 0
			mask  = 3
			width = 2
			shift = 0
		def __init__(self):
			self.vcdrv_offset_9_8 = self._vcdrv_offset_9_8.reset

	class TMF8829_VCDRV_CP(ctypes.LittleEndianStructure):
		addr = 0x3a
		_pack_ = 1
		_fields_ = [
			("vc_spr_spec_amp",ctypes.c_uint8,4),
			("vc_spr_spec_cfg",ctypes.c_uint8,2),
			("vc_spr_spec_single_edge",ctypes.c_uint8,1),
			]
		class _vc_spr_spec_amp:
			reset = 0
			mask  = 15
			width = 4
			shift = 0
		class _vc_spr_spec_cfg:
			reset = 0
			mask  = 48
			width = 2
			shift = 4
			_TFM = 0 # two-frequency mode
			_RFM = 1 # fully random mode
			_RWM = 2 # random walk mode
			_RES = 3 # reserved
		class _vc_spr_spec_single_edge:
			reset = 0
			mask  = 64
			width = 1
			shift = 6
		def __init__(self):
			self.vc_spr_spec_amp = self._vc_spr_spec_amp.reset
			self.vc_spr_spec_cfg = self._vc_spr_spec_cfg.reset
			self.vc_spr_spec_single_edge = self._vc_spr_spec_single_edge.reset

	class TMF8829_HISTOGRAM_BINS_LSB(ctypes.LittleEndianStructure):
		addr = 0x40
		_pack_ = 1
		_fields_ = [
			("histogram_bins_7_0",ctypes.c_uint8,8),
			]
		class _histogram_bins_7_0:
			reset = 218
			mask  = 255
			width = 8
			shift = 0
		def __init__(self):
			self.histogram_bins_7_0 = self._histogram_bins_7_0.reset

	class TMF8829_HISTOGRAM_BINS_MSB(ctypes.LittleEndianStructure):
		addr = 0x41
		_pack_ = 1
		_fields_ = [
			("histogram_bins_9_8",ctypes.c_uint8,2),
			]
		class _histogram_bins_9_8:
			reset = 0
			mask  = 3
			width = 2
			shift = 0
		def __init__(self):
			self.histogram_bins_9_8 = self._histogram_bins_9_8.reset

	class TMF8829_BIN_SHIFT(ctypes.LittleEndianStructure):
		addr = 0x42
		_pack_ = 1
		_fields_ = [
			("bin_shift",ctypes.c_uint8,2),
			]
		class _bin_shift:
			reset = 2
			mask  = 3
			width = 2
			shift = 0
		def __init__(self):
			self.bin_shift = self._bin_shift.reset

	class TMF8829_REF_BIN_SHIFT(ctypes.LittleEndianStructure):
		addr = 0x43
		_pack_ = 1
		_fields_ = [
			("ref_bin_shift",ctypes.c_uint8,2),
			]
		class _ref_bin_shift:
			reset = 2
			mask  = 3
			width = 2
			shift = 0
		def __init__(self):
			self.ref_bin_shift = self._ref_bin_shift.reset

	class TMF8829_TDC_OFFSET_200PS_LSB(ctypes.LittleEndianStructure):
		addr = 0x44
		_pack_ = 1
		_fields_ = [
			("tdc_offset_7_0",ctypes.c_uint8,8),
			]
		class _tdc_offset_7_0:
			reset = 14
			mask  = 255
			width = 8
			shift = 0
		def __init__(self):
			self.tdc_offset_7_0 = self._tdc_offset_7_0.reset

	class TMF8829_TDC_OFFSET_200PS_MSB(ctypes.LittleEndianStructure):
		addr = 0x45
		_pack_ = 1
		_fields_ = [
			("tdc_offset_9_8",ctypes.c_uint8,2),
			]
		class _tdc_offset_9_8:
			reset = 0
			mask  = 3
			width = 2
			shift = 0
		def __init__(self):
			self.tdc_offset_9_8 = self._tdc_offset_9_8.reset

	class TMF8829_TDC_PRE_PERIODS_LSB(ctypes.LittleEndianStructure):
		addr = 0x46
		_pack_ = 1
		_fields_ = [
			("settling_7_0",ctypes.c_uint8,8),
			]
		class _settling_7_0:
			reset = 80
			mask  = 255
			width = 8
			shift = 0
		def __init__(self):
			self.settling_7_0 = self._settling_7_0.reset

	class TMF8829_TDC_PRE_PERIODS_MSB(ctypes.LittleEndianStructure):
		addr = 0x47
		_pack_ = 1
		_fields_ = [
			("settling_9_8",ctypes.c_uint8,2),
			]
		class _settling_9_8:
			reset = 0
			mask  = 3
			width = 2
			shift = 0
		def __init__(self):
			self.settling_9_8 = self._settling_9_8.reset

	class TMF8829_HV_CP(ctypes.LittleEndianStructure):
		addr = 0x48
		_pack_ = 1
		_fields_ = [
			("spr_spec_amp",ctypes.c_uint8,4),
			("spr_spec_cfg",ctypes.c_uint8,2),
			("spr_spec_single_edge",ctypes.c_uint8,1),
			]
		class _spr_spec_amp:
			reset = 0
			mask  = 15
			width = 4
			shift = 0
		class _spr_spec_cfg:
			reset = 0
			mask  = 48
			width = 2
			shift = 4
			_TFM = 0 # two-frequency mode
			_RFM = 1 # fully random mode
			_RWM = 2 # random walk mode
			_REUSE = 3 # reuse VCDRV charge pump clock
		class _spr_spec_single_edge:
			reset = 0
			mask  = 64
			width = 1
			shift = 6
		def __init__(self):
			self.spr_spec_amp = self._spr_spec_amp.reset
			self.spr_spec_cfg = self._spr_spec_cfg.reset
			self.spr_spec_single_edge = self._spr_spec_single_edge.reset

	class TMF8829_CFG_HA_KILO_ITERATIONS_LSB(ctypes.LittleEndianStructure):
		addr = 0x4a
		_pack_ = 1
		_fields_ = [
			("high_accuracy_iterations_7_0",ctypes.c_uint8,8),
			]
		class _high_accuracy_iterations_7_0:
			reset = 100
			mask  = 255
			width = 8
			shift = 0
		def __init__(self):
			self.high_accuracy_iterations_7_0 = self._high_accuracy_iterations_7_0.reset

	class TMF8829_CFG_HA_KILO_ITERATIONS_MSB(ctypes.LittleEndianStructure):
		addr = 0x4b
		_pack_ = 1
		_fields_ = [
			("high_accuracy_iterations_15_8",ctypes.c_uint8,8),
			]
		class _high_accuracy_iterations_15_8:
			reset = 0
			mask  = 255
			width = 8
			shift = 0
		def __init__(self):
			self.high_accuracy_iterations_15_8 = self._high_accuracy_iterations_15_8.reset

	class TMF8829_CFG_ENABLE_DUAL_MODE(ctypes.LittleEndianStructure):
		addr = 0x4c
		_pack_ = 1
		_fields_ = [
			("dual_mode",ctypes.c_uint8,2),
			]
		class _dual_mode:
			reset = 0
			mask  = 3
			width = 2
			shift = 0
			_disabled = 0 # dual-mode is disabled
			_regular_range = 1 # dual-mode is high-accuracy and regular-range-mode (up to 6m)
			_long_range = 2 # dual-mode is high-accuracy and long-range-mode (up to 12m in 8x8 mode only)
			_reserved = 3 # reserved
		def __init__(self):
			self.dual_mode = self._dual_mode.reset

	class TMF8829_CFG_ALG_PEAK_BINS(ctypes.LittleEndianStructure):
		addr = 0x50
		_pack_ = 1
		_fields_ = [
			("peak_bins",ctypes.c_uint8,2),
			]
		class _peak_bins:
			reset = 2
			mask  = 3
			width = 2
			shift = 0
		def __init__(self):
			self.peak_bins = self._peak_bins.reset

	class TMF8829_CFG_ALG_REF_PEAK_BINS(ctypes.LittleEndianStructure):
		addr = 0x51
		_pack_ = 1
		_fields_ = [
			("ref_peak_bins",ctypes.c_uint8,2),
			]
		class _ref_peak_bins:
			reset = 2
			mask  = 3
			width = 2
			shift = 0
		def __init__(self):
			self.ref_peak_bins = self._ref_peak_bins.reset

	class TMF8829_CFG_ALG_DISTANCE(ctypes.LittleEndianStructure):
		addr = 0x52
		_pack_ = 1
		_fields_ = [
			("select",ctypes.c_uint8,2),
			]
		class _select:
			reset = 1
			mask  = 3
			width = 2
			shift = 0
		def __init__(self):
			self.select = self._select.reset

	class TMF8829_CFG_ALG_CONFIDENCE_THRESHOLD(ctypes.LittleEndianStructure):
		addr = 0x53
		_pack_ = 1
		_fields_ = [
			("confidence_threshold",ctypes.c_uint8,8),
			]
		class _confidence_threshold:
			reset = 6
			mask  = 255
			width = 8
			shift = 0
		def __init__(self):
			self.confidence_threshold = self._confidence_threshold.reset

	class TMF8829_CFG_ALG_MIN_SIGNAL_LEVEL_LSB(ctypes.LittleEndianStructure):
		addr = 0x54
		_pack_ = 1
		_fields_ = [
			("signal_level_7_0",ctypes.c_uint8,8),
			]
		class _signal_level_7_0:
			reset = 0
			mask  = 255
			width = 8
			shift = 0
		def __init__(self):
			self.signal_level_7_0 = self._signal_level_7_0.reset

	class TMF8829_CFG_ALG_MIN_SIGNAL_LEVEL_MSB(ctypes.LittleEndianStructure):
		addr = 0x55
		_pack_ = 1
		_fields_ = [
			("signal_level_15_8",ctypes.c_uint8,8),
			]
		class _signal_level_15_8:
			reset = 0
			mask  = 255
			width = 8
			shift = 0
		def __init__(self):
			self.signal_level_15_8 = self._signal_level_15_8.reset

	class TMF8829_CFG_ALG_POISSONADJUST(ctypes.LittleEndianStructure):
		addr = 0x56
		_pack_ = 1
		_fields_ = [
			("poisson",ctypes.c_uint8,8),
			]
		class _poisson:
			reset = 14
			mask  = 255
			width = 8
			shift = 0
		def __init__(self):
			self.poisson = self._poisson.reset

	class TMF8829_CFG_ALG_HW_PEAK_START(ctypes.LittleEndianStructure):
		addr = 0x57
		_pack_ = 1
		_fields_ = [
			("peak_detect_start",ctypes.c_uint8,8),
			]
		class _peak_detect_start:
			reset = 25
			mask  = 255
			width = 8
			shift = 0
		def __init__(self):
			self.peak_detect_start = self._peak_detect_start.reset

	class TMF8829_CFG_ALG_MIN_DISTANCE_LSB(ctypes.LittleEndianStructure):
		addr = 0x58
		_pack_ = 1
		_fields_ = [
			("min_distance_uq_7_0",ctypes.c_uint8,8),
			]
		class _min_distance_uq_7_0:
			reset = 0
			mask  = 255
			width = 8
			shift = 0
		def __init__(self):
			self.min_distance_uq_7_0 = self._min_distance_uq_7_0.reset

	class TMF8829_CFG_ALG_MIN_DISTANCE_MSB(ctypes.LittleEndianStructure):
		addr = 0x59
		_pack_ = 1
		_fields_ = [
			("min_distance_uq_15_8",ctypes.c_uint8,8),
			]
		class _min_distance_uq_15_8:
			reset = 0
			mask  = 255
			width = 8
			shift = 0
		def __init__(self):
			self.min_distance_uq_15_8 = self._min_distance_uq_15_8.reset

	class TMF8829_CFG_ALG_TAIL_MODEL_A_LSB(ctypes.LittleEndianStructure):
		addr = 0x5a
		_pack_ = 1
		_fields_ = [
			("parameter_a_7_0",ctypes.c_uint8,8),
			]
		class _parameter_a_7_0:
			reset = 0
			mask  = 255
			width = 8
			shift = 0
		def __init__(self):
			self.parameter_a_7_0 = self._parameter_a_7_0.reset

	class TMF8829_CFG_ALG_TAIL_MODEL_A_MSB(ctypes.LittleEndianStructure):
		addr = 0x5b
		_pack_ = 1
		_fields_ = [
			("parameter_a_15_8",ctypes.c_uint8,8),
			]
		class _parameter_a_15_8:
			reset = 0
			mask  = 255
			width = 8
			shift = 0
		def __init__(self):
			self.parameter_a_15_8 = self._parameter_a_15_8.reset

	class TMF8829_CFG_ALG_TAIL_MODEL_B_LSB(ctypes.LittleEndianStructure):
		addr = 0x5c
		_pack_ = 1
		_fields_ = [
			("parameter_b_7_0",ctypes.c_uint8,8),
			]
		class _parameter_b_7_0:
			reset = 0
			mask  = 255
			width = 8
			shift = 0
		def __init__(self):
			self.parameter_b_7_0 = self._parameter_b_7_0.reset

	class TMF8829_CFG_ALG_TAIL_MODEL_B_MSB(ctypes.LittleEndianStructure):
		addr = 0x5d
		_pack_ = 1
		_fields_ = [
			("parameter_b_15_8",ctypes.c_uint8,8),
			]
		class _parameter_b_15_8:
			reset = 0
			mask  = 255
			width = 8
			shift = 0
		def __init__(self):
			self.parameter_b_15_8 = self._parameter_b_15_8.reset

	class TMF8829_CFG_ALG_CALIBRATION(ctypes.LittleEndianStructure):
		addr = 0x5f
		_pack_ = 1
		_fields_ = [
			("add_100_mm_offset",ctypes.c_uint8,1),
			]
		class _add_100_mm_offset:
			reset = 0
			mask  = 1
			width = 1
			shift = 0
		def __init__(self):
			self.add_100_mm_offset = self._add_100_mm_offset.reset

	class TMF8829_CFG_INT_ZONE_MASK_0(ctypes.LittleEndianStructure):
		addr = 0x60
		_pack_ = 1
		_fields_ = [
			("int_zone_mask_7_0",ctypes.c_uint8,8),
			]
		class _int_zone_mask_7_0:
			reset = 255
			mask  = 255
			width = 8
			shift = 0
		def __init__(self):
			self.int_zone_mask_7_0 = self._int_zone_mask_7_0.reset

	class TMF8829_CFG_INT_ZONE_MASK_1(ctypes.LittleEndianStructure):
		addr = 0x61
		_pack_ = 1
		_fields_ = [
			("int_zone_mask_15_8",ctypes.c_uint8,8),
			]
		class _int_zone_mask_15_8:
			reset = 255
			mask  = 255
			width = 8
			shift = 0
		def __init__(self):
			self.int_zone_mask_15_8 = self._int_zone_mask_15_8.reset

	class TMF8829_CFG_INT_ZONE_MASK_2(ctypes.LittleEndianStructure):
		addr = 0x62
		_pack_ = 1
		_fields_ = [
			("int_zone_mask_23_16",ctypes.c_uint8,8),
			]
		class _int_zone_mask_23_16:
			reset = 255
			mask  = 255
			width = 8
			shift = 0
		def __init__(self):
			self.int_zone_mask_23_16 = self._int_zone_mask_23_16.reset

	class TMF8829_CFG_INT_ZONE_MASK_3(ctypes.LittleEndianStructure):
		addr = 0x63
		_pack_ = 1
		_fields_ = [
			("int_zone_mask_31_24",ctypes.c_uint8,8),
			]
		class _int_zone_mask_31_24:
			reset = 255
			mask  = 255
			width = 8
			shift = 0
		def __init__(self):
			self.int_zone_mask_31_24 = self._int_zone_mask_31_24.reset

	class TMF8829_CFG_INT_ZONE_MASK_4(ctypes.LittleEndianStructure):
		addr = 0x64
		_pack_ = 1
		_fields_ = [
			("int_zone_mask_39_32",ctypes.c_uint8,8),
			]
		class _int_zone_mask_39_32:
			reset = 255
			mask  = 255
			width = 8
			shift = 0
		def __init__(self):
			self.int_zone_mask_39_32 = self._int_zone_mask_39_32.reset

	class TMF8829_CFG_INT_ZONE_MASK_5(ctypes.LittleEndianStructure):
		addr = 0x65
		_pack_ = 1
		_fields_ = [
			("int_zone_mask_47_40",ctypes.c_uint8,8),
			]
		class _int_zone_mask_47_40:
			reset = 255
			mask  = 255
			width = 8
			shift = 0
		def __init__(self):
			self.int_zone_mask_47_40 = self._int_zone_mask_47_40.reset

	class TMF8829_CFG_INT_ZONE_MASK_6(ctypes.LittleEndianStructure):
		addr = 0x66
		_pack_ = 1
		_fields_ = [
			("int_zone_mask_55_48",ctypes.c_uint8,8),
			]
		class _int_zone_mask_55_48:
			reset = 255
			mask  = 255
			width = 8
			shift = 0
		def __init__(self):
			self.int_zone_mask_55_48 = self._int_zone_mask_55_48.reset

	class TMF8829_CFG_INT_ZONE_MASK_7(ctypes.LittleEndianStructure):
		addr = 0x67
		_pack_ = 1
		_fields_ = [
			("int_zone_mask_63_56",ctypes.c_uint8,8),
			]
		class _int_zone_mask_63_56:
			reset = 255
			mask  = 255
			width = 8
			shift = 0
		def __init__(self):
			self.int_zone_mask_63_56 = self._int_zone_mask_63_56.reset

	class TMF8829_CFG_INT_THRESHOLD_LOW_LSB(ctypes.LittleEndianStructure):
		addr = 0x68
		_pack_ = 1
		_fields_ = [
			("int_threshold_low_7_0",ctypes.c_uint8,8),
			]
		class _int_threshold_low_7_0:
			reset = 0
			mask  = 255
			width = 8
			shift = 0
		def __init__(self):
			self.int_threshold_low_7_0 = self._int_threshold_low_7_0.reset

	class TMF8829_CFG_INT_THRESHOLD_LOW_MSB(ctypes.LittleEndianStructure):
		addr = 0x69
		_pack_ = 1
		_fields_ = [
			("int_threshold_low_15_8",ctypes.c_uint8,8),
			]
		class _int_threshold_low_15_8:
			reset = 0
			mask  = 255
			width = 8
			shift = 0
		def __init__(self):
			self.int_threshold_low_15_8 = self._int_threshold_low_15_8.reset

	class TMF8829_CFG_INT_THRESHOLD_HIGH_LSB(ctypes.LittleEndianStructure):
		addr = 0x6a
		_pack_ = 1
		_fields_ = [
			("int_threshold_high_7_0",ctypes.c_uint8,8),
			]
		class _int_threshold_high_7_0:
			reset = 255
			mask  = 255
			width = 8
			shift = 0
		def __init__(self):
			self.int_threshold_high_7_0 = self._int_threshold_high_7_0.reset

	class TMF8829_CFG_INT_THRESHOLD_HIGH_MSB(ctypes.LittleEndianStructure):
		addr = 0x6b
		_pack_ = 1
		_fields_ = [
			("int_threshold_high_15_8",ctypes.c_uint8,8),
			]
		class _int_threshold_high_15_8:
			reset = 255
			mask  = 255
			width = 8
			shift = 0
		def __init__(self):
			self.int_threshold_high_15_8 = self._int_threshold_high_15_8.reset

	class TMF8829_CFG_INT_PERSISTENCE(ctypes.LittleEndianStructure):
		addr = 0x6c
		_pack_ = 1
		_fields_ = [
			("int_persistence",ctypes.c_uint8,8),
			]
		class _int_persistence:
			reset = 0
			mask  = 255
			width = 8
			shift = 0
		def __init__(self):
			self.int_persistence = self._int_persistence.reset

	class TMF8829_CFG_POST_PROCESSING(ctypes.LittleEndianStructure):
		addr = 0x6d
		_pack_ = 1
		_fields_ = [
			("post_processing",ctypes.c_uint8,8),
			]
		class _post_processing:
			reset = 0
			mask  = 255
			width = 8
			shift = 0
			_PERSISTENCE = 0 # persistence algorithm enabled
			_MOTION = 1 # motion detection, (also int_persistence must be set to >=1 in field TMF8829_CFG_INT_PERSISTENCE)
		def __init__(self):
			self.post_processing = self._post_processing.reset

	class TMF8829_CFG_CROP_TOP_X(ctypes.LittleEndianStructure):
		addr = 0x70
		_pack_ = 1
		_fields_ = [
			("mp_top_x",ctypes.c_uint8,4),
			]
		class _mp_top_x:
			reset = 0
			mask  = 15
			width = 4
			shift = 0
		def __init__(self):
			self.mp_top_x = self._mp_top_x.reset

	class TMF8829_CFG_CROP_TOP_Y(ctypes.LittleEndianStructure):
		addr = 0x71
		_pack_ = 1
		_fields_ = [
			("mp_top_y",ctypes.c_uint8,4),
			]
		class _mp_top_y:
			reset = 0
			mask  = 15
			width = 4
			shift = 0
		def __init__(self):
			self.mp_top_y = self._mp_top_y.reset

	class TMF8829_CFG_CROP_BOTTOM_X(ctypes.LittleEndianStructure):
		addr = 0x72
		_pack_ = 1
		_fields_ = [
			("mp_bottom_x",ctypes.c_uint8,4),
			]
		class _mp_bottom_x:
			reset = 15
			mask  = 15
			width = 4
			shift = 0
		def __init__(self):
			self.mp_bottom_x = self._mp_bottom_x.reset

	class TMF8829_CFG_CROP_BOTTOM_Y(ctypes.LittleEndianStructure):
		addr = 0x73
		_pack_ = 1
		_fields_ = [
			("mp_bottom_y",ctypes.c_uint8,4),
			]
		class _mp_bottom_y:
			reset = 15
			mask  = 15
			width = 4
			shift = 0
		def __init__(self):
			self.mp_bottom_y = self._mp_bottom_y.reset

	class TMF8829_CFG_CROP_REFERENCE(ctypes.LittleEndianStructure):
		addr = 0x74
		_pack_ = 1
		_fields_ = [
			("ref_mp",ctypes.c_uint8,4),
			]
		class _ref_mp:
			reset = 15
			mask  = 15
			width = 4
			shift = 0
		def __init__(self):
			self.ref_mp = self._ref_mp.reset

	class TMF8829_CFG_INFO_FOV_CORR(ctypes.LittleEndianStructure):
		addr = 0x78
		_pack_ = 1
		_fields_ = [
			("fov_correction",ctypes.c_uint8,4),
			]
		class _fov_correction:
			reset = 0
			mask  = 15
			width = 4
			shift = 0
		def __init__(self):
			self.fov_correction = self._fov_correction.reset

	class TMF8829_CFG_GPIO_0(ctypes.LittleEndianStructure):
		addr = 0x80
		_pack_ = 1
		_fields_ = [
			("gpio0",ctypes.c_uint8,3),
			]
		class _gpio0:
			reset = 0
			mask  = 7
			width = 3
			shift = 0
			_TRISTATE = 0 # pin is in tristate
			_INPUT_IR = 1 # pin is input and IR output follows logical level (i.e. if high, IR output is on, else off)
			_INPUT_ACTIVE_HIGH = 2 # pin is input and active high
			_INPUT_ACTIVE_LOW = 3 # pin is input active low
			_OUTPUT_LOW_VCSEL_PULSING = 4 # pin is output low while VCSEL is pulsing
			_OUTPUT_HIGH_VCSEL_PULSING = 5 # pin is output high while VCSEL pulsing
			_OUTPUT_HIGH = 6 # pin is constant high
			_OUTPUT_LOW = 7 # pin is constant low
		def __init__(self):
			self.gpio0 = self._gpio0.reset

	class TMF8829_CFG_GPIO_1(ctypes.LittleEndianStructure):
		addr = 0x81
		_pack_ = 1
		_fields_ = [
			("gpio1",ctypes.c_uint8,3),
			]
		class _gpio1:
			reset = 0
			mask  = 7
			width = 3
			shift = 0
			_TRISTATE = 0 # pin is in tristate
			_INPUT_IR = 1 # pin is input and IR output follows logical level (i.e. if high, IR output is on, else off)
			_INPUT_ACTIVE_HIGH = 2 # pin is input and active high
			_INPUT_ACTIVE_LOW = 3 # pin is input active low
			_OUTPUT_LOW_VCSEL_PULSING = 4 # pin is output low while VCSEL is pulsing
			_OUTPUT_HIGH_VCSEL_PULSING = 5 # pin is output high while VCSEL pulsing
			_OUTPUT_HIGH = 6 # pin is constant high
			_OUTPUT_LOW = 7 # pin is constant low
		def __init__(self):
			self.gpio1 = self._gpio1.reset

	class TMF8829_CFG_GPIO_2(ctypes.LittleEndianStructure):
		addr = 0x82
		_pack_ = 1
		_fields_ = [
			("gpio2",ctypes.c_uint8,3),
			]
		class _gpio2:
			reset = 0
			mask  = 7
			width = 3
			shift = 0
			_TRISTATE = 0 # pin is in tristate
			_INPUT_IR = 1 # pin is input and IR output follows logical level (i.e. if high, IR output is on, else off)
			_INPUT_ACTIVE_HIGH = 2 # pin is input and active high
			_INPUT_ACTIVE_LOW = 3 # pin is input active low
			_OUTPUT_LOW_VCSEL_PULSING = 4 # pin is output low while VCSEL is pulsing
			_OUTPUT_HIGH_VCSEL_PULSING = 5 # pin is output high while VCSEL pulsing
			_OUTPUT_HIGH = 6 # pin is constant high
			_OUTPUT_LOW = 7 # pin is constant low
		def __init__(self):
			self.gpio2 = self._gpio2.reset

	class TMF8829_CFG_GPIO_3(ctypes.LittleEndianStructure):
		addr = 0x83
		_pack_ = 1
		_fields_ = [
			("gpio3",ctypes.c_uint8,3),
			]
		class _gpio3:
			reset = 0
			mask  = 7
			width = 3
			shift = 0
			_TRISTATE = 0 # pin is in tristate
			_INPUT_IR = 1 # pin is input and IR output follows logical level (i.e. if high, IR output is on, else off)
			_INPUT_ACTIVE_HIGH = 2 # pin is input and active high
			_INPUT_ACTIVE_LOW = 3 # pin is input active low
			_OUTPUT_LOW_VCSEL_PULSING = 4 # pin is output low while VCSEL is pulsing
			_OUTPUT_HIGH_VCSEL_PULSING = 5 # pin is output high while VCSEL pulsing
			_OUTPUT_HIGH = 6 # pin is constant high
			_OUTPUT_LOW = 7 # pin is constant low
		def __init__(self):
			self.gpio3 = self._gpio3.reset

	class TMF8829_CFG_GPIO_4(ctypes.LittleEndianStructure):
		addr = 0x84
		_pack_ = 1
		_fields_ = [
			("gpio4",ctypes.c_uint8,3),
			]
		class _gpio4:
			reset = 0
			mask  = 7
			width = 3
			shift = 0
			_TRISTATE = 0 # pin is in tristate
			_INPUT_IR = 1 # pin is input and IR output follows logical level (i.e. if high, IR output is on, else off)
			_INPUT_ACTIVE_HIGH = 2 # pin is input and active high
			_INPUT_ACTIVE_LOW = 3 # pin is input active low
			_OUTPUT_LOW_VCSEL_PULSING = 4 # pin is output low while VCSEL is pulsing
			_OUTPUT_HIGH_VCSEL_PULSING = 5 # pin is output high while VCSEL pulsing
			_OUTPUT_HIGH = 6 # pin is constant high
			_OUTPUT_LOW = 7 # pin is constant low
		def __init__(self):
			self.gpio4 = self._gpio4.reset

	class TMF8829_CFG_GPIO_5(ctypes.LittleEndianStructure):
		addr = 0x85
		_pack_ = 1
		_fields_ = [
			("gpio5",ctypes.c_uint8,3),
			]
		class _gpio5:
			reset = 0
			mask  = 7
			width = 3
			shift = 0
			_TRISTATE = 0 # pin is in tristate
			_INPUT_IR = 1 # pin is input and IR output follows logical level (i.e. if high, IR output is on, else off)
			_INPUT_ACTIVE_HIGH = 2 # pin is input and active high
			_INPUT_ACTIVE_LOW = 3 # pin is input active low
			_OUTPUT_LOW_VCSEL_PULSING = 4 # pin is output low while VCSEL is pulsing
			_OUTPUT_HIGH_VCSEL_PULSING = 5 # pin is output high while VCSEL pulsing
			_OUTPUT_HIGH = 6 # pin is constant high
			_OUTPUT_LOW = 7 # pin is constant low
		def __init__(self):
			self.gpio5 = self._gpio5.reset

	class TMF8829_CFG_GPIO_6(ctypes.LittleEndianStructure):
		addr = 0x86
		_pack_ = 1
		_fields_ = [
			("gpio6",ctypes.c_uint8,3),
			]
		class _gpio6:
			reset = 0
			mask  = 7
			width = 3
			shift = 0
			_TRISTATE = 0 # pin is in tristate
			_INPUT_IR = 1 # pin is input and IR output follows logical level (i.e. if high, IR output is on, else off)
			_INPUT_ACTIVE_HIGH = 2 # pin is input and active high
			_INPUT_ACTIVE_LOW = 3 # pin is input active low
			_OUTPUT_LOW_VCSEL_PULSING = 4 # pin is output low while VCSEL is pulsing
			_OUTPUT_HIGH_VCSEL_PULSING = 5 # pin is output high while VCSEL pulsing
			_OUTPUT_HIGH = 6 # pin is constant high
			_OUTPUT_LOW = 7 # pin is constant low
		def __init__(self):
			self.gpio6 = self._gpio6.reset

	class TMF8829_CFG_GPIO(ctypes.LittleEndianStructure):
		addr = 0x87
		_pack_ = 1
		_fields_ = [
			("pre_delay",ctypes.c_uint8,2),
			]
		class _pre_delay:
			reset = 0
			mask  = 3
			width = 2
			shift = 0
			_NO_PREDELAY = 0 # No predelay
			_d_100_US_PREDELAY = 1 # 100 microseconds pre-delay
			_d_200_US_PREDELAY = 2 # 200 microseconds pre-delay
		def __init__(self):
			self.pre_delay = self._pre_delay.reset

	class TMF8829_CFG_I2C_ADDRESS(ctypes.LittleEndianStructure):
		addr = 0x90
		_pack_ = 1
		_fields_ = [
			("i2c_slave_address",ctypes.c_uint8,8),
			]
		class _i2c_slave_address:
			reset = 130
			mask  = 255
			width = 8
			shift = 0
		def __init__(self):
			self.i2c_slave_address = self._i2c_slave_address.reset

	class TMF8829_CFG_ALG_XTALK_DISTANCE_MM(ctypes.LittleEndianStructure):
		addr = 0xa0
		_pack_ = 1
		_fields_ = [
			("xtalk_distance_mm",ctypes.c_uint8,8),
			]
		class _xtalk_distance_mm:
			reset = 0
			mask  = 255
			width = 8
			shift = 0
		def __init__(self):
			self.xtalk_distance_mm = self._xtalk_distance_mm.reset

	class TMF8829_CFG_ALG_XTALK_MAX_LSB(ctypes.LittleEndianStructure):
		addr = 0xa2
		_pack_ = 1
		_fields_ = [
			("xtalk_max_7_0",ctypes.c_uint8,8),
			]
		class _xtalk_max_7_0:
			reset = 0
			mask  = 255
			width = 8
			shift = 0
		def __init__(self):
			self.xtalk_max_7_0 = self._xtalk_max_7_0.reset

	class TMF8829_CFG_ALG_XTALK_MAX_MSB(ctypes.LittleEndianStructure):
		addr = 0xa3
		_pack_ = 1
		_fields_ = [
			("xtalk_max_15_8",ctypes.c_uint8,8),
			]
		class _xtalk_max_15_8:
			reset = 0
			mask  = 255
			width = 8
			shift = 0
		def __init__(self):
			self.xtalk_max_15_8 = self._xtalk_max_15_8.reset

	class TMF8829_CFG_ALG_XTALK_EDGE_LSB(ctypes.LittleEndianStructure):
		addr = 0xa4
		_pack_ = 1
		_fields_ = [
			("xtalk_edge_7_0",ctypes.c_uint8,8),
			]
		class _xtalk_edge_7_0:
			reset = 187
			mask  = 255
			width = 8
			shift = 0
		def __init__(self):
			self.xtalk_edge_7_0 = self._xtalk_edge_7_0.reset

	class TMF8829_CFG_ALG_XTALK_EDGE_MSB(ctypes.LittleEndianStructure):
		addr = 0xa5
		_pack_ = 1
		_fields_ = [
			("xtalk_edge_15_8",ctypes.c_uint8,8),
			]
		class _xtalk_edge_15_8:
			reset = 0
			mask  = 255
			width = 8
			shift = 0
		def __init__(self):
			self.xtalk_edge_15_8 = self._xtalk_edge_15_8.reset

	class TMF8829_CFG_MOTION_DETECT_DISTANCE_LSB(ctypes.LittleEndianStructure):
		addr = 0xb0
		_pack_ = 1
		_fields_ = [
			("motion_distance_7_0",ctypes.c_uint8,8),
			]
		class _motion_distance_7_0:
			reset = 208
			mask  = 255
			width = 8
			shift = 0
		def __init__(self):
			self.motion_distance_7_0 = self._motion_distance_7_0.reset

	class TMF8829_CFG_MOTION_DETECT_DISTANCE_MSB(ctypes.LittleEndianStructure):
		addr = 0xb1
		_pack_ = 1
		_fields_ = [
			("motion_distance_15_8",ctypes.c_uint8,8),
			]
		class _motion_distance_15_8:
			reset = 7
			mask  = 255
			width = 8
			shift = 0
		def __init__(self):
			self.motion_distance_15_8 = self._motion_distance_15_8.reset

	class TMF8829_CFG_MOTION_DETECT_SNR(ctypes.LittleEndianStructure):
		addr = 0xb2
		_pack_ = 1
		_fields_ = [
			("detect_snr",ctypes.c_uint8,8),
			]
		class _detect_snr:
			reset = 10
			mask  = 255
			width = 8
			shift = 0
		def __init__(self):
			self.detect_snr = self._detect_snr.reset

	class TMF8829_CFG_MOTION_RELEASE_SNR(ctypes.LittleEndianStructure):
		addr = 0xb3
		_pack_ = 1
		_fields_ = [
			("release_snr",ctypes.c_uint8,8),
			]
		class _release_snr:
			reset = 6
			mask  = 255
			width = 8
			shift = 0
		def __init__(self):
			self.release_snr = self._release_snr.reset

	class TMF8829_CFG_MOTION_ADJACENT_PIXEL(ctypes.LittleEndianStructure):
		addr = 0xb4
		_pack_ = 1
		_fields_ = [
			("motion_adjacent",ctypes.c_uint8,4),
			]
		class _motion_adjacent:
			reset = 8
			mask  = 15
			width = 4
			shift = 0
		def __init__(self):
			self.motion_adjacent = self._motion_adjacent.reset

	class TMF8829_CFG_LAST_AVAILABLE(ctypes.LittleEndianStructure):
		addr = 0xdf
		_pack_ = 1
		_fields_ = [
			("last_cfg_register",ctypes.c_uint8,8),
			]
		class _last_cfg_register:
			reset = 0
			mask  = 255
			width = 8
			shift = 0
		def __init__(self):
			self.last_cfg_register = self._last_cfg_register.reset


	def __init__(self):
		self.TMF8829_CFG_PERIOD_MS_LSB = Tmf8829_config_page.TMF8829_CFG_PERIOD_MS_LSB()
		self.TMF8829_CFG_PERIOD_MS_MSB = Tmf8829_config_page.TMF8829_CFG_PERIOD_MS_MSB()
		self.TMF8829_CFG_KILO_ITERATIONS_LSB = Tmf8829_config_page.TMF8829_CFG_KILO_ITERATIONS_LSB()
		self.TMF8829_CFG_KILO_ITERATIONS_MSB = Tmf8829_config_page.TMF8829_CFG_KILO_ITERATIONS_MSB()
		self.TMF8829_CFG_FP_MODE = Tmf8829_config_page.TMF8829_CFG_FP_MODE()
		self.TMF8829_CFG_SPAD_SELECT = Tmf8829_config_page.TMF8829_CFG_SPAD_SELECT()
		self.TMF8829_CFG_REF_SPAD_SELECT = Tmf8829_config_page.TMF8829_CFG_REF_SPAD_SELECT()
		self.TMF8829_CFG_SPAD_DEADTIME = Tmf8829_config_page.TMF8829_CFG_SPAD_DEADTIME()
		self.TMF8829_CFG_RESULT_FORMAT = Tmf8829_config_page.TMF8829_CFG_RESULT_FORMAT()
		self.TMF8829_CFG_DUMP_HISTOGRAMS = Tmf8829_config_page.TMF8829_CFG_DUMP_HISTOGRAMS()
		self.TMF8829_CFG_REF_SPAD_FRAME = Tmf8829_config_page.TMF8829_CFG_REF_SPAD_FRAME()
		self.TMF8829_CFG_TEMP_SENSOR = Tmf8829_config_page.TMF8829_CFG_TEMP_SENSOR()
		self.TMF8829_CFG_POWER_MODES = Tmf8829_config_page.TMF8829_CFG_POWER_MODES()
		self.TMF8829_CFG_VCSEL_ON = Tmf8829_config_page.TMF8829_CFG_VCSEL_ON()
		self.TMF8829_CFG_DITHER = Tmf8829_config_page.TMF8829_CFG_DITHER()
		self.TMF8829_CFG_VCDRV = Tmf8829_config_page.TMF8829_CFG_VCDRV()
		self.TMF8829_CFG_VCDRV_2 = Tmf8829_config_page.TMF8829_CFG_VCDRV_2()
		self.TMF8829_CFG_VCDRV_3 = Tmf8829_config_page.TMF8829_CFG_VCDRV_3()
		self.TMF8829_VCSEL_PERIOD_200PS_LSB = Tmf8829_config_page.TMF8829_VCSEL_PERIOD_200PS_LSB()
		self.TMF8829_VCSEL_PERIOD_200PS_MSB = Tmf8829_config_page.TMF8829_VCSEL_PERIOD_200PS_MSB()
		self.TMF8829_VCDRV_OFFSET_200PS_LSB = Tmf8829_config_page.TMF8829_VCDRV_OFFSET_200PS_LSB()
		self.TMF8829_VCDRV_OFFSET_200PS_MSB = Tmf8829_config_page.TMF8829_VCDRV_OFFSET_200PS_MSB()
		self.TMF8829_VCDRV_CP = Tmf8829_config_page.TMF8829_VCDRV_CP()
		self.TMF8829_HISTOGRAM_BINS_LSB = Tmf8829_config_page.TMF8829_HISTOGRAM_BINS_LSB()
		self.TMF8829_HISTOGRAM_BINS_MSB = Tmf8829_config_page.TMF8829_HISTOGRAM_BINS_MSB()
		self.TMF8829_BIN_SHIFT = Tmf8829_config_page.TMF8829_BIN_SHIFT()
		self.TMF8829_REF_BIN_SHIFT = Tmf8829_config_page.TMF8829_REF_BIN_SHIFT()
		self.TMF8829_TDC_OFFSET_200PS_LSB = Tmf8829_config_page.TMF8829_TDC_OFFSET_200PS_LSB()
		self.TMF8829_TDC_OFFSET_200PS_MSB = Tmf8829_config_page.TMF8829_TDC_OFFSET_200PS_MSB()
		self.TMF8829_TDC_PRE_PERIODS_LSB = Tmf8829_config_page.TMF8829_TDC_PRE_PERIODS_LSB()
		self.TMF8829_TDC_PRE_PERIODS_MSB = Tmf8829_config_page.TMF8829_TDC_PRE_PERIODS_MSB()
		self.TMF8829_HV_CP = Tmf8829_config_page.TMF8829_HV_CP()
		self.TMF8829_CFG_HA_KILO_ITERATIONS_LSB = Tmf8829_config_page.TMF8829_CFG_HA_KILO_ITERATIONS_LSB()
		self.TMF8829_CFG_HA_KILO_ITERATIONS_MSB = Tmf8829_config_page.TMF8829_CFG_HA_KILO_ITERATIONS_MSB()
		self.TMF8829_CFG_ENABLE_DUAL_MODE = Tmf8829_config_page.TMF8829_CFG_ENABLE_DUAL_MODE()
		self.TMF8829_CFG_ALG_PEAK_BINS = Tmf8829_config_page.TMF8829_CFG_ALG_PEAK_BINS()
		self.TMF8829_CFG_ALG_REF_PEAK_BINS = Tmf8829_config_page.TMF8829_CFG_ALG_REF_PEAK_BINS()
		self.TMF8829_CFG_ALG_DISTANCE = Tmf8829_config_page.TMF8829_CFG_ALG_DISTANCE()
		self.TMF8829_CFG_ALG_CONFIDENCE_THRESHOLD = Tmf8829_config_page.TMF8829_CFG_ALG_CONFIDENCE_THRESHOLD()
		self.TMF8829_CFG_ALG_MIN_SIGNAL_LEVEL_LSB = Tmf8829_config_page.TMF8829_CFG_ALG_MIN_SIGNAL_LEVEL_LSB()
		self.TMF8829_CFG_ALG_MIN_SIGNAL_LEVEL_MSB = Tmf8829_config_page.TMF8829_CFG_ALG_MIN_SIGNAL_LEVEL_MSB()
		self.TMF8829_CFG_ALG_POISSONADJUST = Tmf8829_config_page.TMF8829_CFG_ALG_POISSONADJUST()
		self.TMF8829_CFG_ALG_HW_PEAK_START = Tmf8829_config_page.TMF8829_CFG_ALG_HW_PEAK_START()
		self.TMF8829_CFG_ALG_MIN_DISTANCE_LSB = Tmf8829_config_page.TMF8829_CFG_ALG_MIN_DISTANCE_LSB()
		self.TMF8829_CFG_ALG_MIN_DISTANCE_MSB = Tmf8829_config_page.TMF8829_CFG_ALG_MIN_DISTANCE_MSB()
		self.TMF8829_CFG_ALG_TAIL_MODEL_A_LSB = Tmf8829_config_page.TMF8829_CFG_ALG_TAIL_MODEL_A_LSB()
		self.TMF8829_CFG_ALG_TAIL_MODEL_A_MSB = Tmf8829_config_page.TMF8829_CFG_ALG_TAIL_MODEL_A_MSB()
		self.TMF8829_CFG_ALG_TAIL_MODEL_B_LSB = Tmf8829_config_page.TMF8829_CFG_ALG_TAIL_MODEL_B_LSB()
		self.TMF8829_CFG_ALG_TAIL_MODEL_B_MSB = Tmf8829_config_page.TMF8829_CFG_ALG_TAIL_MODEL_B_MSB()
		self.TMF8829_CFG_ALG_CALIBRATION = Tmf8829_config_page.TMF8829_CFG_ALG_CALIBRATION()
		self.TMF8829_CFG_INT_ZONE_MASK_0 = Tmf8829_config_page.TMF8829_CFG_INT_ZONE_MASK_0()
		self.TMF8829_CFG_INT_ZONE_MASK_1 = Tmf8829_config_page.TMF8829_CFG_INT_ZONE_MASK_1()
		self.TMF8829_CFG_INT_ZONE_MASK_2 = Tmf8829_config_page.TMF8829_CFG_INT_ZONE_MASK_2()
		self.TMF8829_CFG_INT_ZONE_MASK_3 = Tmf8829_config_page.TMF8829_CFG_INT_ZONE_MASK_3()
		self.TMF8829_CFG_INT_ZONE_MASK_4 = Tmf8829_config_page.TMF8829_CFG_INT_ZONE_MASK_4()
		self.TMF8829_CFG_INT_ZONE_MASK_5 = Tmf8829_config_page.TMF8829_CFG_INT_ZONE_MASK_5()
		self.TMF8829_CFG_INT_ZONE_MASK_6 = Tmf8829_config_page.TMF8829_CFG_INT_ZONE_MASK_6()
		self.TMF8829_CFG_INT_ZONE_MASK_7 = Tmf8829_config_page.TMF8829_CFG_INT_ZONE_MASK_7()
		self.TMF8829_CFG_INT_THRESHOLD_LOW_LSB = Tmf8829_config_page.TMF8829_CFG_INT_THRESHOLD_LOW_LSB()
		self.TMF8829_CFG_INT_THRESHOLD_LOW_MSB = Tmf8829_config_page.TMF8829_CFG_INT_THRESHOLD_LOW_MSB()
		self.TMF8829_CFG_INT_THRESHOLD_HIGH_LSB = Tmf8829_config_page.TMF8829_CFG_INT_THRESHOLD_HIGH_LSB()
		self.TMF8829_CFG_INT_THRESHOLD_HIGH_MSB = Tmf8829_config_page.TMF8829_CFG_INT_THRESHOLD_HIGH_MSB()
		self.TMF8829_CFG_INT_PERSISTENCE = Tmf8829_config_page.TMF8829_CFG_INT_PERSISTENCE()
		self.TMF8829_CFG_POST_PROCESSING = Tmf8829_config_page.TMF8829_CFG_POST_PROCESSING()
		self.TMF8829_CFG_CROP_TOP_X = Tmf8829_config_page.TMF8829_CFG_CROP_TOP_X()
		self.TMF8829_CFG_CROP_TOP_Y = Tmf8829_config_page.TMF8829_CFG_CROP_TOP_Y()
		self.TMF8829_CFG_CROP_BOTTOM_X = Tmf8829_config_page.TMF8829_CFG_CROP_BOTTOM_X()
		self.TMF8829_CFG_CROP_BOTTOM_Y = Tmf8829_config_page.TMF8829_CFG_CROP_BOTTOM_Y()
		self.TMF8829_CFG_CROP_REFERENCE = Tmf8829_config_page.TMF8829_CFG_CROP_REFERENCE()
		self.TMF8829_CFG_INFO_FOV_CORR = Tmf8829_config_page.TMF8829_CFG_INFO_FOV_CORR()
		self.TMF8829_CFG_GPIO_0 = Tmf8829_config_page.TMF8829_CFG_GPIO_0()
		self.TMF8829_CFG_GPIO_1 = Tmf8829_config_page.TMF8829_CFG_GPIO_1()
		self.TMF8829_CFG_GPIO_2 = Tmf8829_config_page.TMF8829_CFG_GPIO_2()
		self.TMF8829_CFG_GPIO_3 = Tmf8829_config_page.TMF8829_CFG_GPIO_3()
		self.TMF8829_CFG_GPIO_4 = Tmf8829_config_page.TMF8829_CFG_GPIO_4()
		self.TMF8829_CFG_GPIO_5 = Tmf8829_config_page.TMF8829_CFG_GPIO_5()
		self.TMF8829_CFG_GPIO_6 = Tmf8829_config_page.TMF8829_CFG_GPIO_6()
		self.TMF8829_CFG_GPIO = Tmf8829_config_page.TMF8829_CFG_GPIO()
		self.TMF8829_CFG_I2C_ADDRESS = Tmf8829_config_page.TMF8829_CFG_I2C_ADDRESS()
		self.TMF8829_CFG_ALG_XTALK_DISTANCE_MM = Tmf8829_config_page.TMF8829_CFG_ALG_XTALK_DISTANCE_MM()
		self.TMF8829_CFG_ALG_XTALK_MAX_LSB = Tmf8829_config_page.TMF8829_CFG_ALG_XTALK_MAX_LSB()
		self.TMF8829_CFG_ALG_XTALK_MAX_MSB = Tmf8829_config_page.TMF8829_CFG_ALG_XTALK_MAX_MSB()
		self.TMF8829_CFG_ALG_XTALK_EDGE_LSB = Tmf8829_config_page.TMF8829_CFG_ALG_XTALK_EDGE_LSB()
		self.TMF8829_CFG_ALG_XTALK_EDGE_MSB = Tmf8829_config_page.TMF8829_CFG_ALG_XTALK_EDGE_MSB()
		self.TMF8829_CFG_MOTION_DETECT_DISTANCE_LSB = Tmf8829_config_page.TMF8829_CFG_MOTION_DETECT_DISTANCE_LSB()
		self.TMF8829_CFG_MOTION_DETECT_DISTANCE_MSB = Tmf8829_config_page.TMF8829_CFG_MOTION_DETECT_DISTANCE_MSB()
		self.TMF8829_CFG_MOTION_DETECT_SNR = Tmf8829_config_page.TMF8829_CFG_MOTION_DETECT_SNR()
		self.TMF8829_CFG_MOTION_RELEASE_SNR = Tmf8829_config_page.TMF8829_CFG_MOTION_RELEASE_SNR()
		self.TMF8829_CFG_MOTION_ADJACENT_PIXEL = Tmf8829_config_page.TMF8829_CFG_MOTION_ADJACENT_PIXEL()
		self.TMF8829_CFG_LAST_AVAILABLE = Tmf8829_config_page.TMF8829_CFG_LAST_AVAILABLE()

