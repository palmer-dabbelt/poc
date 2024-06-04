# SPDX-License-Identifier: GPL-2.0-only OR GPL-3.0-only

from amaranth import *
from amaranth.lib import wiring
from amaranth.lib.wiring import In, Out, Component, connect
from amaranth.lib.enum import Enum

from frontend import Frontend

from memport import MemPortSource

class CoreRunState(Enum, shape=int(2)):
	RESET = 0
	RUNNING = 1
	SUCCESS = 2
	FAIL = 3

class Core(Component):
	state: Out(CoreRunState)
	valid_bytes: In(7)

	def __init__(self):
		self.memport = MemPortSource(64, 512)
		super().__init__()

	def elaborate(self, platform):
		m = Module()

		actually_valid = Signal()
		m.d.sync += actually_valid.eq(self.memport.res.valid.bool() & (self.valid_bytes > 0).bool())

		frontend = Frontend()
		m.submodules.frontend = frontend
		m.d.sync += [
			frontend.icache_refill.req.ready.eq(self.memport.req.ready),
			self.memport.req.valid.eq(frontend.icache_refill.req.valid),
			self.memport.req.addr.eq(frontend.icache_refill.req.addr),
			self.memport.res.ready.eq(frontend.icache_refill.res.ready),
			frontend.icache_refill.res.valid.eq(self.memport.res.valid),
			frontend.icache_refill.res.data.eq(self.memport.res.data),
		]

		with m.If(frontend.valid & frontend.ready):
			with m.If(frontend.instruction == 0x00000073):
				m.d.sync += self.state.eq(CoreRunState.SUCCESS)
			with m.Elif(frontend.instruction == 0x0000007E):
				m.d.sync += self.state.eq(CoreRunState.FAIL)
			with m.Else():
				m.d.sync += self.state.eq(CoreRunState.RUNNING)
		with m.Elif(self.state == CoreRunState.RESET):
			m.d.sync += self.state.eq(CoreRunState.RUNNING)

		m.d.comb += frontend.ready.eq(self.state == CoreRunState.RUNNING)

		return m
