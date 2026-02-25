# *****************************************************************************
# * Copyright by ams OSRAM AG                                                 *
# * All rights are reserved.                                                  *
# *                                                                           *
# *FOR FULL LICENSE TEXT SEE LICENSES-MIT.TXT                                 *
# *****************************************************************************

import ctypes

class Tmf8829_application_registers:

	addr_width = 6
	data_width = 8

	class TMF8829_APP_ID(ctypes.LittleEndianStructure):
		addr = 0x00
		_pack_ = 1
		_fields_ = [
			("appid",ctypes.c_uint8,8),
			]
		class _appid:
			reset = 1
			mask  = 255
			width = 8
			shift = 0
			_BOOTLOADER = 128 # bootloader application ID
			_APPLICATION = 2 # ROM application ID for version 2
		def __init__(self):
			self.appid = self._appid.reset

	class TMF8829_MAJOR(ctypes.LittleEndianStructure):
		addr = 0x01
		_pack_ = 1
		_fields_ = [
			("major",ctypes.c_uint8,8),
			]
		class _major:
			reset = 0
			mask  = 255
			width = 8
			shift = 0
		def __init__(self):
			self.major = self._major.reset

	class TMF8829_MINOR(ctypes.LittleEndianStructure):
		addr = 0x02
		_pack_ = 1
		_fields_ = [
			("minor",ctypes.c_uint8,8),
			]
		class _minor:
			reset = 0
			mask  = 255
			width = 8
			shift = 0
		def __init__(self):
			self.minor = self._minor.reset

	class TMF8829_CAPABILITIES(ctypes.LittleEndianStructure):
		addr = 0x03
		_pack_ = 1
		_fields_ = [
			("capabilities",ctypes.c_uint8,8),
			]
		class _capabilities:
			reset = 0
			mask  = 255
			width = 8
			shift = 0
		def __init__(self):
			self.capabilities = self._capabilities.reset

	class TMF8829_APPLICATION_STATUS(ctypes.LittleEndianStructure):
		addr = 0x04
		_pack_ = 1
		_fields_ = [
			("app_status",ctypes.c_uint8,8),
			]
		class _app_status:
			reset = 0
			mask  = 255
			width = 8
			shift = 0
			_SUCCESS = 0 # application has no error
		def __init__(self):
			self.app_status = self._app_status.reset

	class TMF8829_MEASURE_STATUS(ctypes.LittleEndianStructure):
		addr = 0x05
		_pack_ = 1
		_fields_ = [
			("measure_status",ctypes.c_uint8,8),
			]
		class _measure_status:
			reset = 0
			mask  = 255
			width = 8
			shift = 0
			_SUCCESS = 0 # measurement state machine has no error
		def __init__(self):
			self.measure_status = self._measure_status.reset

	class TMF8829_ALGORITHM_STATUS(ctypes.LittleEndianStructure):
		addr = 0x06
		_pack_ = 1
		_fields_ = [
			("alg_status",ctypes.c_uint8,8),
			]
		class _alg_status:
			reset = 0
			mask  = 255
			width = 8
			shift = 0
			_SUCCESS = 0 # algorithm has no error
		def __init__(self):
			self.alg_status = self._alg_status.reset

	class TMF8829_CALIBRATION_STATUS(ctypes.LittleEndianStructure):
		addr = 0x07
		_pack_ = 1
		_fields_ = [
			("calib_status",ctypes.c_uint8,8),
			]
		class _calib_status:
			reset = 0
			mask  = 255
			width = 8
			shift = 0
			_SUCCESS = 0 # calibration data available
		def __init__(self):
			self.calib_status = self._calib_status.reset

	class TMF8829_CMD_STAT(ctypes.LittleEndianStructure):
		addr = 0x08
		_pack_ = 1
		_fields_ = [
			("cmd_stat",ctypes.c_uint8,8),
			]
		class _cmd_stat:
			reset = 0
			mask  = 255
			width = 8
			shift = 0
			_CMD_MEASURE = 16 # Measure: start a cyclic measurement according to the configuration
			_CMD_CLEAR_STATUS = 17 # Clear Status: clear all status registers (note that a new measurement clears them too)
			_CMD_WRITE_PAGE_AND_MEASURE = 20 # Write Configuration page (whatever page has been loaded to registers 0x20 and following will be written to the device) and start a measurement (if no error occured)
			_CMD_WRITE_PAGE = 21 # Write Configuration page (whatever page has been loaded to registers 0x20 and following will be written to the device)
			_CMD_LOAD_CONFIG_PAGE = 22 # Load Configuration Page configuration
			_CMD_LOAD_DIAGNOSTIC_PAGE = 23 # Load diagnostic Page configuration
			_CMD_LOAD_CALIBRATION_PAGE = 24 # Load calibration page (TBD)
			_CMD_OSC_TUNE_UP = 30 # increase power to oscillator == tune faster (not monoton increasing)
			_CMD_OSC_TUNE_DOWN = 31 # decrease power to oscillator == tune slower (not monoton decreasing)
			_CMD_LOAD_CFG_8X8 = 64 # Preconfigure for 8x8 default mode and load configuration page
			_CMD_LOAD_CFG_8X8_LONG_RANGE = 65 # Preconfigure for 8x8 12m mode and load configuration page
			_CMD_LOAD_CFG_8X8_HIGH_ACCURACY = 66 # Preconfigure for 8x8 (short range mode) higher resolution = better visibility at short range and load configuration page
			_CMD_LOAD_CFG_16X16 = 67 # Preconfigure for 16x16 default mode and load configuration page
			_CMD_LOAD_CFG_16X16_HIGH_ACCURACY = 68 # Preconfigure for 16x16 short range mode and load configuration page
			_CMD_LOAD_CFG_32X32 = 69 # Preconfigure for 32x32 default mode and load configuration page
			_CMD_LOAD_CFG_32X32_HIGH_ACCURACY = 70 # Preconfigure for 32x32 short range mode and load configuration page
			_CMD_LOAD_CFG_48X32 = 71 # Preconfigure for 48x32 default mode and load configuration page
			_CMD_LOAD_CFG_48X32_HIGH_ACCURACY = 72 # Preconfigure for 48x32 short range mode and load configuration page
			_CMD_R_HW = 128 # Read from a 4-byte address
			_CMD_W_HW = 129 # Write a 4-byte value to a 4-byte address
			_CMD_W_HW_MASK = 130 # Write a 4-byte masked value to a 4-byte address
			_CMD_STOP = 255 # Stop: abort any ongoing measurement
			_STAT_OK = 0 # Ok, command accepted and successfully executed
			_STAT_ACCEPTED = 1 # Command accepted and being executed, must send a STOP command to halt continues execution
			_STAT_ERR_CONFIG = 2 # ERROR configuration not accepted, reconfiguration neeede
			_STAT_ERR_APPLICATION = 3 # ERROR application encountered a severe error and stopped
			_STAT_ERR_CONFIG_RESULT_SIZE = 4 # ERROR configuration will generate result frames that are too big to be transferred
			_STAT_ERR_CONFIG_VCSEL = 5 # ERROR configuration of VCSEL (only one of the two can be on at one point in time)
			_STAT_ERR_WAKEUP_TIMED = 6 # ERROR wakeup timed, severe internal error, device should be power cycled
			_STAT_ERR_RESET_UNEXPECTED = 7 # ERROR unexpected reset, severe internal error, device should be power cycles
			_STAT_ERR_UNKNOWN_CMD = 8 # ERROR unknown command
			_STAT_ERR_UNKNOWN_CID = 9 # ERROR tried to write a config page with unknown CID
			_STAT_ERR_STOP_0 = 10 # ERROR stop not accepted by cpu0, do a power cycle
			_STAT_ERR_STOP_1 = 11 # ERROR stop not accepted by cpu1, do a power cycle
			_STAT_ERR_STOP_2 = 12 # ERROR stop not accepted by cpu0 and cpu1, do a power cycle
			_STAT_ERR_STOP_3 = 13 # ERROR stop not handled by IRQ handler, do a power cycle
			_STAT_ERR_OSC_TUNE = 14 # ERROR could not increase or decrease the oscillator tune value
		def __init__(self):
			self.cmd_stat = self._cmd_stat.reset

	class TMF8829_PREV_CMD(ctypes.LittleEndianStructure):
		addr = 0x09
		_pack_ = 1
		_fields_ = [
			("prev_cmd",ctypes.c_uint8,8),
			]
		class _prev_cmd:
			reset = 0
			mask  = 255
			width = 8
			shift = 0
		def __init__(self):
			self.prev_cmd = self._prev_cmd.reset

	class TMF8829_GPIO_VALUE(ctypes.LittleEndianStructure):
		addr = 0x10
		_pack_ = 1
		_fields_ = [
			("gpio_value",ctypes.c_uint8,7),
			]
		class _gpio_value:
			reset = 0
			mask  = 127
			width = 7
			shift = 0
		def __init__(self):
			self.gpio_value = self._gpio_value.reset

	class TMF8829_LIVE_BEAT_0(ctypes.LittleEndianStructure):
		addr = 0x1a
		_pack_ = 1
		_fields_ = [
			("live_beat_0",ctypes.c_uint8,8),
			]
		class _live_beat_0:
			reset = 0
			mask  = 255
			width = 8
			shift = 0
		def __init__(self):
			self.live_beat_0 = self._live_beat_0.reset

	class TMF8829_LIVE_BEAT_1(ctypes.LittleEndianStructure):
		addr = 0x1b
		_pack_ = 1
		_fields_ = [
			("live_beat_1",ctypes.c_uint8,8),
			]
		class _live_beat_1:
			reset = 0
			mask  = 255
			width = 8
			shift = 0
		def __init__(self):
			self.live_beat_1 = self._live_beat_1.reset

	class TMF8829_SERIAL_NUMBER_0(ctypes.LittleEndianStructure):
		addr = 0x1c
		_pack_ = 1
		_fields_ = [
			("serial_number_7_0",ctypes.c_uint8,8),
			]
		class _serial_number_7_0:
			reset = 0
			mask  = 255
			width = 8
			shift = 0
		def __init__(self):
			self.serial_number_7_0 = self._serial_number_7_0.reset

	class TMF8829_SERIAL_NUMBER_1(ctypes.LittleEndianStructure):
		addr = 0x1d
		_pack_ = 1
		_fields_ = [
			("serial_number_15_8",ctypes.c_uint8,8),
			]
		class _serial_number_15_8:
			reset = 0
			mask  = 255
			width = 8
			shift = 0
		def __init__(self):
			self.serial_number_15_8 = self._serial_number_15_8.reset

	class TMF8829_SERIAL_NUMBER_2(ctypes.LittleEndianStructure):
		addr = 0x1e
		_pack_ = 1
		_fields_ = [
			("serial_number_23_16",ctypes.c_uint8,8),
			]
		class _serial_number_23_16:
			reset = 0
			mask  = 255
			width = 8
			shift = 0
		def __init__(self):
			self.serial_number_23_16 = self._serial_number_23_16.reset

	class TMF8829_SERIAL_NUMBER_3(ctypes.LittleEndianStructure):
		addr = 0x1f
		_pack_ = 1
		_fields_ = [
			("serial_number_31_24",ctypes.c_uint8,8),
			]
		class _serial_number_31_24:
			reset = 0
			mask  = 255
			width = 8
			shift = 0
		def __init__(self):
			self.serial_number_31_24 = self._serial_number_31_24.reset

	class TMF8829_CID_RID(ctypes.LittleEndianStructure):
		addr = 0x20
		_pack_ = 1
		_fields_ = [
			("cid_rid",ctypes.c_uint8,8),
			]
		class _cid_rid:
			reset = 0
			mask  = 255
			width = 8
			shift = 0
			_CID_CONFIG = 22 # Config page is loaded
			_CID_DIAGNOSTIC = 23 # Diagnostic page is loaded
			_CID_CALIBRATION = 24 # Calibration page is loaded
			_RID_REF_SPAD_FRAME = 48 # Reference spad frame ID
			_CID_CFG_8X8 = 64 # Preconfigure for 8x8 default mode page
			_CID_CFG_8X8_LONG_RANGE = 65 # Preconfigure for 8x8 12m mode page
			_CID_CFG_8X8_HIGH_ACCURACY = 66 # Preconfigure for 8x8 (short range mode) higher resolution page
			_CID_CFG_16X16 = 67 # Preconfigure for 16x16 default mode  page
			_CID_CFG_16X16_HIGH_ACCURACY = 68 # Preconfigure for 16x16 short range mode  page
			_CID_CFG_32X32 = 69 # Preconfigure for 32x32 default mode page
			_CID_CFG_32X32_HIGH_ACCURACY = 70 # Preconfigure for 32x32 short range mode page
			_CID_CFG_48X32 = 71 # Preconfigure for 48x32 default mode page
			_CID_CFG_48X32_HIGH_ACCURACY = 72 # Preconfigure for 48x32 short range mode page
		def __init__(self):
			self.cid_rid = self._cid_rid.reset

	class TMF8829_PAYLOAD(ctypes.LittleEndianStructure):
		addr = 0x21
		_pack_ = 1
		_fields_ = [
			("payload",ctypes.c_uint8,8),
			]
		class _payload:
			reset = 190
			mask  = 255
			width = 8
			shift = 0
		def __init__(self):
			self.payload = self._payload.reset


	def __init__(self):
		self.TMF8829_APP_ID = Tmf8829_application_registers.TMF8829_APP_ID()
		self.TMF8829_MAJOR = Tmf8829_application_registers.TMF8829_MAJOR()
		self.TMF8829_MINOR = Tmf8829_application_registers.TMF8829_MINOR()
		self.TMF8829_CAPABILITIES = Tmf8829_application_registers.TMF8829_CAPABILITIES()
		self.TMF8829_APPLICATION_STATUS = Tmf8829_application_registers.TMF8829_APPLICATION_STATUS()
		self.TMF8829_MEASURE_STATUS = Tmf8829_application_registers.TMF8829_MEASURE_STATUS()
		self.TMF8829_ALGORITHM_STATUS = Tmf8829_application_registers.TMF8829_ALGORITHM_STATUS()
		self.TMF8829_CALIBRATION_STATUS = Tmf8829_application_registers.TMF8829_CALIBRATION_STATUS()
		self.TMF8829_CMD_STAT = Tmf8829_application_registers.TMF8829_CMD_STAT()
		self.TMF8829_PREV_CMD = Tmf8829_application_registers.TMF8829_PREV_CMD()
		self.TMF8829_GPIO_VALUE = Tmf8829_application_registers.TMF8829_GPIO_VALUE()
		self.TMF8829_LIVE_BEAT_0 = Tmf8829_application_registers.TMF8829_LIVE_BEAT_0()
		self.TMF8829_LIVE_BEAT_1 = Tmf8829_application_registers.TMF8829_LIVE_BEAT_1()
		self.TMF8829_SERIAL_NUMBER_0 = Tmf8829_application_registers.TMF8829_SERIAL_NUMBER_0()
		self.TMF8829_SERIAL_NUMBER_1 = Tmf8829_application_registers.TMF8829_SERIAL_NUMBER_1()
		self.TMF8829_SERIAL_NUMBER_2 = Tmf8829_application_registers.TMF8829_SERIAL_NUMBER_2()
		self.TMF8829_SERIAL_NUMBER_3 = Tmf8829_application_registers.TMF8829_SERIAL_NUMBER_3()
		self.TMF8829_CID_RID = Tmf8829_application_registers.TMF8829_CID_RID()
		self.TMF8829_PAYLOAD = Tmf8829_application_registers.TMF8829_PAYLOAD()

