# SPDX-License-Identifier: GPL-2.0-only OR GPL-3.0-only

from amaranth import *
from amaranth.lib import wiring
from amaranth.lib.wiring import In, Out, Component, connect
from amaranth.lib.enum import Enum

from frontend import Frontend

from memport import MemPortSignature

from pms import Buffer

class CoreRunState(Enum, shape=int(2)):
	RESET = 0
	RUNNING = 1
	SUCCESS = 2
	FAIL = 3

class Core(Component):
	def __init__(self):
		super().__init__({
			"state": Out(CoreRunState),
			"valid_bytes": In(7),
			"memport": Out(MemPortSignature(64, 512)),
		})

	def elaborate(self, platform):
		m = Module()

		actually_valid = Signal()
		m.d.sync += actually_valid.eq(self.memport.res.valid & (self.valid_bytes > 0))
		
		m.submodules.frontend = frontend = Frontend()

		# For now our whole memory system is just a buffer.  That's
		# probably good enough for a little while.
		membuf = Buffer(m, self.memport, frontend.icache_refill)

		# This roles the whole backend into basically just decode logic: 
		m.d.comb += frontend.ready.eq(self.state == CoreRunState.RUNNING)
		with m.If(frontend.valid & frontend.ready):
			with m.If(frontend.instruction == 0x00000073):
				m.d.sync += self.state.eq(CoreRunState.SUCCESS)
			with m.Elif(frontend.instruction == 0x0000007E):
				m.d.sync += self.state.eq(CoreRunState.FAIL)
			with m.Else():
				m.d.sync += self.state.eq(CoreRunState.RUNNING)
		with m.Elif(self.state == CoreRunState.RESET):
			m.d.sync += self.state.eq(CoreRunState.RUNNING)


		return m
