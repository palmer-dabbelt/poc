# SPDX-License-Identifier: GPL-2.0-only OR GPL-3.0-only

from amaranth import *
from amaranth.lib import wiring
from amaranth.lib.wiring import In, Out, Component
from amaranth.lib.enum import Enum

from frontend import Frontend

class CoreRunState(Enum, shape=2):
	RESET = 0
	RUNNING = 1
	SUCCESS = 2
	FAIL = 3

class Core(Component):
	# FIXME: No idea why I can't just do a "Out(CoreRunState)" here...
	state: Out(2)

	def __init__(self):
		super().__init__()

	def elaborate(self, platform):
		m = Module()

		m.submodules.frontend = frontend = Frontend()

		with m.If(frontend.valid):
			with m.If(frontend.instruction == 0x0000007F):
				m.d.sync += self.state.eq(CoreRunState.SUCCESS)
			with m.If(frontend.instruction == 0x0000007E):
				m.d.sync += self.state.eq(CoreRunState.FAIL)

		return m
