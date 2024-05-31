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

	# ... and also no idea why I can't just do a "mem_port:
	# MemPortSource(64, 512)" here.  Maybe there's some issue with
	# non-primitive types at the top level?  The docs say something about
	# IOPort.
	req_ready: In(1)
	req_valid: Out(1)
	req_addr:  Out(64)
	res_ready: Out(1)
	res_valid: In(1)
	res_data:  In(512)

	def __init__(self):
		# FIXME: Also not sure why I have to do this here, as opposed
		# to as a static member as above.
		#self.mem_port = MemPortSource(64, 512)
		super().__init__()

	def elaborate(self, platform):
		m = Module()

		frontend = Frontend()
		m.submodules.frontend = frontend
		m.d.sync += [
			frontend.icache_refill.req.ready.eq(self.req_ready),
			self.req_valid.eq(frontend.icache_refill.req.valid),
			self.req_addr.eq(frontend.icache_refill.req.addr),
			self.res_ready.eq(frontend.icache_refill.res.ready),
			frontend.icache_refill.res.valid.eq(self.res_valid),
			frontend.icache_refill.res.data.eq(self.res_data),
		]

		with m.If(frontend.valid):
			with m.If(frontend.instruction == 0x00000073):
				m.d.sync += self.state.eq(CoreRunState.SUCCESS)
			with m.If(frontend.instruction == 0x0000007E):
				m.d.sync += self.state.eq(CoreRunState.FAIL)

		return m
