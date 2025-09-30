# *****************************************************************************
# * Copyright by ams OSRAM AG                                                 *
# * All rights are reserved.                                                  *
# *                                                                           *
# *FOR FULL LICENSE TEXT SEE LICENSES-MIT.TXT                                 *
# *****************************************************************************

import ctypes

class Tmf8829_host_regs:

	addr_width = 8
	data_width = 8

	class I2C_DEVADDR(ctypes.LittleEndianStructure):
		addr = 0xe0
		_pack_ = 1
		_fields_ = [
			("enab_ack_hdr_write",ctypes.c_uint8,1),
			("i2c_devaddr",ctypes.c_uint8,7),
			]
		class _enab_ack_hdr_write:
			reset = 0
			mask  = 1
			width = 1
			shift = 0
		class _i2c_devaddr:
			reset = 65
			mask  = 254
			width = 7
			shift = 1
		def __init__(self):
			self.enab_ack_hdr_write = self._enab_ack_hdr_write.reset
			self.i2c_devaddr = self._i2c_devaddr.reset

	class INT_STATUS(ctypes.LittleEndianStructure):
		addr = 0xe1
		_pack_ = 1
		_fields_ = [
			("int0",ctypes.c_uint8,1),
			("int1",ctypes.c_uint8,1),
			("int2",ctypes.c_uint8,1),
			("int3",ctypes.c_uint8,1),
			("int4",ctypes.c_uint8,1),
			("int5",ctypes.c_uint8,1),
			("int6",ctypes.c_uint8,1),
			("int7",ctypes.c_uint8,1),
			]
		class _int0:
			reset = 0
			mask  = 1
			width = 1
			shift = 0
		class _int1:
			reset = 0
			mask  = 2
			width = 1
			shift = 1
		class _int2:
			reset = 0
			mask  = 4
			width = 1
			shift = 2
		class _int3:
			reset = 0
			mask  = 8
			width = 1
			shift = 3
		class _int4:
			reset = 0
			mask  = 16
			width = 1
			shift = 4
		class _int5:
			reset = 0
			mask  = 32
			width = 1
			shift = 5
		class _int6:
			reset = 0
			mask  = 64
			width = 1
			shift = 6
		class _int7:
			reset = 0
			mask  = 128
			width = 1
			shift = 7
		def __init__(self):
			self.int0 = self._int0.reset
			self.int1 = self._int1.reset
			self.int2 = self._int2.reset
			self.int3 = self._int3.reset
			self.int4 = self._int4.reset
			self.int5 = self._int5.reset
			self.int6 = self._int6.reset
			self.int7 = self._int7.reset

	class INT_ENAB(ctypes.LittleEndianStructure):
		addr = 0xe2
		_pack_ = 1
		_fields_ = [
			("int0_enab",ctypes.c_uint8,1),
			("int1_enab",ctypes.c_uint8,1),
			("int2_enab",ctypes.c_uint8,1),
			("int3_enab",ctypes.c_uint8,1),
			("int4_enab",ctypes.c_uint8,1),
			("int5_enab",ctypes.c_uint8,1),
			("int6_enab",ctypes.c_uint8,1),
			("int7_enab",ctypes.c_uint8,1),
			]
		class _int0_enab:
			reset = 0
			mask  = 1
			width = 1
			shift = 0
		class _int1_enab:
			reset = 0
			mask  = 2
			width = 1
			shift = 1
		class _int2_enab:
			reset = 0
			mask  = 4
			width = 1
			shift = 2
		class _int3_enab:
			reset = 0
			mask  = 8
			width = 1
			shift = 3
		class _int4_enab:
			reset = 0
			mask  = 16
			width = 1
			shift = 4
		class _int5_enab:
			reset = 0
			mask  = 32
			width = 1
			shift = 5
		class _int6_enab:
			reset = 0
			mask  = 64
			width = 1
			shift = 6
		class _int7_enab:
			reset = 0
			mask  = 128
			width = 1
			shift = 7
		def __init__(self):
			self.int0_enab = self._int0_enab.reset
			self.int1_enab = self._int1_enab.reset
			self.int2_enab = self._int2_enab.reset
			self.int3_enab = self._int3_enab.reset
			self.int4_enab = self._int4_enab.reset
			self.int5_enab = self._int5_enab.reset
			self.int6_enab = self._int6_enab.reset
			self.int7_enab = self._int7_enab.reset

	class ID(ctypes.LittleEndianStructure):
		addr = 0xe3
		_pack_ = 1
		_fields_ = [
			("device_id",ctypes.c_uint8,8),
			]
		class _device_id:
			reset = 158
			mask  = 255
			width = 8
			shift = 0
		def __init__(self):
			self.device_id = self._device_id.reset

	class REVID(ctypes.LittleEndianStructure):
		addr = 0xe4
		_pack_ = 1
		_fields_ = [
			("rev_id",ctypes.c_uint8,3),
			]
		class _rev_id:
			reset = 0
			mask  = 7
			width = 3
			shift = 0
		def __init__(self):
			self.rev_id = self._rev_id.reset

	class GPIO01CFG(ctypes.LittleEndianStructure):
		addr = 0xf1
		_pack_ = 1
		_fields_ = [
			("gpio0_func",ctypes.c_uint8,4),
			("gpio1_func",ctypes.c_uint8,4),
			]
		class _gpio0_func:
			reset = 1
			mask  = 15
			width = 4
			shift = 0
			_GPIO0 = 0 # GPIO0
			_MOSI = 1 # SPI MOSI (serial data input)
			_SWD0 = 2 # Serial Wire Debug Interface 0, Data input/output
			_UART = 3 # UART transmit data
			_VCDRV = 4 # VCSEL driving pulse
			_VCSELIN = 5 # VCSEL pulse input
			_TMX0 = 8 # Testmux0
			_TMX1 = 9 # Testmux1
			_TMX2 = 10 # Testmux2
			_TMX3 = 11 # Testmux3
			_PADTMX0 = 12 # Padtestmux0
			_PADTMX1 = 13 # Padtestmux1
		class _gpio1_func:
			reset = 1
			mask  = 240
			width = 4
			shift = 4
			_GPIO1 = 0 # GPIO1
			_CSN = 1 # SPI CSN (chips select input)
			_SWC0 = 2 # Serial Wire Debug Interface 0, Clock inputw
			_UART = 3 # UART transmit data
			_VCDRV = 4 # VCSEL driving pulse
			_VCSELIN = 5 # VCSEL pulse input
			_TMX0 = 8 # Testmux0
			_TMX1 = 9 # Testmux1
			_TMX2 = 10 # Testmux2
			_TMX3 = 11 # Testmux3
			_PADTMX0 = 12 # Padtestmux0
			_PADTMX1 = 13 # Padtestmux1
		def __init__(self):
			self.gpio0_func = self._gpio0_func.reset
			self.gpio1_func = self._gpio1_func.reset

	class GPIO23CFG(ctypes.LittleEndianStructure):
		addr = 0xf2
		_pack_ = 1
		_fields_ = [
			("gpio2_func",ctypes.c_uint8,4),
			("gpio3_func",ctypes.c_uint8,4),
			]
		class _gpio2_func:
			reset = 1
			mask  = 15
			width = 4
			shift = 0
			_GPIO2 = 0 # GPIO2
			_SCLK = 1 # SPI SCLK (serial clock input)
			_SWD1 = 2 # Serial Wire Debug Interface 1, Data input/output
			_UART = 3 # UART transmit data
			_VCDRV = 4 # VCSEL driving pulse
			_VCSELIN = 5 # VCSEL pulse input
			_TMX0 = 8 # Testmux0
			_TMX1 = 9 # Testmux1
			_TMX2 = 10 # Testmux2
			_TMX3 = 11 # Testmux3
			_PADTMX0 = 12 # Padtestmux0
			_PADTMX1 = 13 # Padtestmux1
		class _gpio3_func:
			reset = 1
			mask  = 240
			width = 4
			shift = 4
			_GPIO3 = 0 # GPIO3
			_MISO = 1 # SPI MISO (serial data output)
			_SWC1 = 2 # Serial Wire Debug Interface 1, Clock input
			_UART = 3 # UART transmit data
			_VCDRV = 4 # VCSEL driving pulse
			_VCSELIN = 5 # VCSEL pulse input
			_TMX0 = 8 # Testmux0
			_TMX1 = 9 # Testmux1
			_TMX2 = 10 # Testmux2
			_TMX3 = 11 # Testmux3
			_PADTMX0 = 12 # Padtestmux0
			_PADTMX1 = 13 # Padtestmux1
		def __init__(self):
			self.gpio2_func = self._gpio2_func.reset
			self.gpio3_func = self._gpio3_func.reset

	class GPIO45CFG(ctypes.LittleEndianStructure):
		addr = 0xf3
		_pack_ = 1
		_fields_ = [
			("gpio4_func",ctypes.c_uint8,4),
			("gpio5_func",ctypes.c_uint8,4),
			]
		class _gpio4_func:
			reset = 1
			mask  = 15
			width = 4
			shift = 0
			_GPIO4 = 0 # GPIO4
			_SCL = 1 # I2C/I3C SCL (serial clock input)
			_SWD0 = 2 # Serial Wire Debug Interface 0, Data input/output
			_UART = 3 # UART transmit data
			_VCDRV = 4 # VCSEL driving pulse
			_VCSELIN = 5 # VCSEL pulse input
			_TMX0 = 8 # Testmux0
			_TMX1 = 9 # Testmux1
			_TMX2 = 10 # Testmux2
			_TMX3 = 11 # Testmux3
			_PADTMX0 = 12 # Padtestmux0
			_PADTMX1 = 13 # Padtestmux1
		class _gpio5_func:
			reset = 1
			mask  = 240
			width = 4
			shift = 4
			_GPIO5 = 0 # GPIO5
			_SDA = 1 # I2C/I3C SDA (serial data input/output)
			_SWC0 = 2 # Serial Wire Debug Interface 0, Clock input
			_UART = 3 # UART transmit data
			_VCDRV = 4 # VCSEL driving pulse
			_VCSELIN = 5 # VCSEL pulse input
			_TMX0 = 8 # Testmux0
			_TMX1 = 9 # Testmux1
			_TMX2 = 10 # Testmux2
			_TMX3 = 11 # Testmux3
			_PADTMX0 = 12 # Padtestmux0
			_PADTMX1 = 13 # Padtestmux1
		def __init__(self):
			self.gpio4_func = self._gpio4_func.reset
			self.gpio5_func = self._gpio5_func.reset

	class GPIO6CFG(ctypes.LittleEndianStructure):
		addr = 0xf4
		_pack_ = 1
		_fields_ = [
			("gpio6_func",ctypes.c_uint8,4),
			]
		class _gpio6_func:
			reset = 1
			mask  = 15
			width = 4
			shift = 0
			_GPIO6 = 0 # GPIO6
			_INT = 1 # INT (low active interrupt)
			_UART = 3 # UART transmit data
			_VCDRV = 4 # VCSEL driving pulse
			_VCSELIN = 5 # VCSEL pulse input
			_TMX0 = 8 # Testmux0
			_TMX1 = 9 # Testmux1
			_TMX2 = 10 # Testmux2
			_TMX3 = 11 # Testmux3
			_PADTMX0 = 12 # Padtestmux0
			_PADTMX1 = 13 # Padtestmux1
		def __init__(self):
			self.gpio6_func = self._gpio6_func.reset

	class RESET(ctypes.LittleEndianStructure):
		addr = 0xf7
		_pack_ = 1
		_fields_ = [
			("reset_reason_timer",ctypes.c_uint8,1),
			("reset_reason_host",ctypes.c_uint8,1),
			("RESET_resv_2",ctypes.c_uint8,1),
			("reset_reason_soft_reset",ctypes.c_uint8,1),
			("reset_reason_hard_reset",ctypes.c_uint8,1),
			("reset_reason_coldstart",ctypes.c_uint8,1),
			("soft_reset",ctypes.c_uint8,1),
			("hard_reset",ctypes.c_uint8,1),
			]
		class _reset_reason_timer:
			reset = 0
			mask  = 1
			width = 1
			shift = 0
		class _reset_reason_host:
			reset = 0
			mask  = 2
			width = 1
			shift = 1
		class _RESET_resv_2:
			reset = 0
			mask  = 0
			width = 0
			shift = 0
		class _reset_reason_soft_reset:
			reset = 0
			mask  = 8
			width = 1
			shift = 3
		class _reset_reason_hard_reset:
			reset = 0
			mask  = 16
			width = 1
			shift = 4
		class _reset_reason_coldstart:
			reset = 1
			mask  = 32
			width = 1
			shift = 5
		class _soft_reset:
			reset = 0
			mask  = 64
			width = 1
			shift = 6
		class _hard_reset:
			reset = 0
			mask  = 128
			width = 1
			shift = 7
		def __init__(self):
			self.reset_reason_timer = self._reset_reason_timer.reset
			self.reset_reason_host = self._reset_reason_host.reset
			self.RESET_resv_2 = self._RESET_resv_2.reset
			self.reset_reason_soft_reset = self._reset_reason_soft_reset.reset
			self.reset_reason_hard_reset = self._reset_reason_hard_reset.reset
			self.reset_reason_coldstart = self._reset_reason_coldstart.reset
			self.soft_reset = self._soft_reset.reset
			self.hard_reset = self._hard_reset.reset

	class ENABLE(ctypes.LittleEndianStructure):
		addr = 0xf8
		_pack_ = 1
		_fields_ = [
			("standby_mode",ctypes.c_uint8,1),
			("timed_standby_mode",ctypes.c_uint8,1),
			("pon",ctypes.c_uint8,1),
			("poff",ctypes.c_uint8,1),
			("powerup_select",ctypes.c_uint8,2),
			("bootwithoutpll",ctypes.c_uint8,1),
			("cpu_ready",ctypes.c_uint8,1),
			]
		class _standby_mode:
			reset = 0
			mask  = 1
			width = 1
			shift = 0
		class _timed_standby_mode:
			reset = 0
			mask  = 2
			width = 1
			shift = 1
		class _pon:
			reset = 1
			mask  = 4
			width = 1
			shift = 2
		class _poff:
			reset = 0
			mask  = 8
			width = 1
			shift = 3
		class _powerup_select:
			reset = 0
			mask  = 48
			width = 2
			shift = 4
			_NO_OVERRIDE = 0 # No override - use content of fuses to select - see boot-matrix above (default)
			_FORCE_BOOTMONITOR = 1 # Force bootmonitor - ignore fuses and wait for host commands
			_RAM = 2 # execute AORAM bootrecords and then set IVT to 0x10000 (base of RAM)to RAM and start whatever application is there - no checks are done!! - application in RAM has to check for reset-reason to know how to proceed
		class _bootwithoutpll:
			reset = 0
			mask  = 64
			width = 1
			shift = 6
		class _cpu_ready:
			reset = 0
			mask  = 128
			width = 1
			shift = 7
		def __init__(self):
			self.standby_mode = self._standby_mode.reset
			self.timed_standby_mode = self._timed_standby_mode.reset
			self.pon = self._pon.reset
			self.poff = self._poff.reset
			self.powerup_select = self._powerup_select.reset
			self.bootwithoutpll = self._bootwithoutpll.reset
			self.cpu_ready = self._cpu_ready.reset

	class FIFOSTATUS(ctypes.LittleEndianStructure):
		addr = 0xfa
		_pack_ = 1
		_fields_ = [
			("fifo_direction",ctypes.c_uint8,1),
			("fifo_dma_busy",ctypes.c_uint8,1),
			("txfifo_empty",ctypes.c_uint8,1),
			("rxfifo_full",ctypes.c_uint8,1),
			("txfifo_underrun",ctypes.c_uint8,1),
			("rxfifo_overrun",ctypes.c_uint8,1),
			]
		class _fifo_direction:
			reset = 0
			mask  = 1
			width = 1
			shift = 0
		class _fifo_dma_busy:
			reset = 0
			mask  = 2
			width = 1
			shift = 1
		class _txfifo_empty:
			reset = 1
			mask  = 4
			width = 1
			shift = 2
		class _rxfifo_full:
			reset = 0
			mask  = 8
			width = 1
			shift = 3
		class _txfifo_underrun:
			reset = 0
			mask  = 16
			width = 1
			shift = 4
		class _rxfifo_overrun:
			reset = 0
			mask  = 32
			width = 1
			shift = 5
		def __init__(self):
			self.fifo_direction = self._fifo_direction.reset
			self.fifo_dma_busy = self._fifo_dma_busy.reset
			self.txfifo_empty = self._txfifo_empty.reset
			self.rxfifo_full = self._rxfifo_full.reset
			self.txfifo_underrun = self._txfifo_underrun.reset
			self.rxfifo_overrun = self._rxfifo_overrun.reset

	class SYSTICK_0(ctypes.LittleEndianStructure):
		addr = 0xfb
		_pack_ = 1
		_fields_ = [
			("hif_systick_7_0",ctypes.c_uint8,8),
			]
		class _hif_systick_7_0:
			reset = 0
			mask  = 255
			width = 8
			shift = 0
		def __init__(self):
			self.hif_systick_7_0 = self._hif_systick_7_0.reset

	class SYSTICK_1(ctypes.LittleEndianStructure):
		addr = 0xfc
		_pack_ = 1
		_fields_ = [
			("hif_systick_15_8",ctypes.c_uint8,8),
			]
		class _hif_systick_15_8:
			reset = 0
			mask  = 255
			width = 8
			shift = 0
		def __init__(self):
			self.hif_systick_15_8 = self._hif_systick_15_8.reset

	class SYSTICK_2(ctypes.LittleEndianStructure):
		addr = 0xfd
		_pack_ = 1
		_fields_ = [
			("hif_systick_23_16",ctypes.c_uint8,8),
			]
		class _hif_systick_23_16:
			reset = 0
			mask  = 255
			width = 8
			shift = 0
		def __init__(self):
			self.hif_systick_23_16 = self._hif_systick_23_16.reset

	class SYSTICK_3(ctypes.LittleEndianStructure):
		addr = 0xfe
		_pack_ = 1
		_fields_ = [
			("hif_systick_31_24",ctypes.c_uint8,8),
			]
		class _hif_systick_31_24:
			reset = 0
			mask  = 255
			width = 8
			shift = 0
		def __init__(self):
			self.hif_systick_31_24 = self._hif_systick_31_24.reset

	class FIFO(ctypes.LittleEndianStructure):
		addr = 0xff
		_pack_ = 1
		_fields_ = [
			("fifo_data",ctypes.c_uint8,8),
			]
		class _fifo_data:
			reset = 0
			mask  = 255
			width = 8
			shift = 0
		def __init__(self):
			self.fifo_data = self._fifo_data.reset


	def __init__(self):
		self.I2C_DEVADDR = Tmf8829_host_regs.I2C_DEVADDR()
		self.INT_STATUS = Tmf8829_host_regs.INT_STATUS()
		self.INT_ENAB = Tmf8829_host_regs.INT_ENAB()
		self.ID = Tmf8829_host_regs.ID()
		self.REVID = Tmf8829_host_regs.REVID()
		self.GPIO01CFG = Tmf8829_host_regs.GPIO01CFG()
		self.GPIO23CFG = Tmf8829_host_regs.GPIO23CFG()
		self.GPIO45CFG = Tmf8829_host_regs.GPIO45CFG()
		self.GPIO6CFG = Tmf8829_host_regs.GPIO6CFG()
		self.RESET = Tmf8829_host_regs.RESET()
		self.ENABLE = Tmf8829_host_regs.ENABLE()
		self.FIFOSTATUS = Tmf8829_host_regs.FIFOSTATUS()
		self.SYSTICK_0 = Tmf8829_host_regs.SYSTICK_0()
		self.SYSTICK_1 = Tmf8829_host_regs.SYSTICK_1()
		self.SYSTICK_2 = Tmf8829_host_regs.SYSTICK_2()
		self.SYSTICK_3 = Tmf8829_host_regs.SYSTICK_3()
		self.FIFO = Tmf8829_host_regs.FIFO()

