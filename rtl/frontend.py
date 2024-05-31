# SPDX-License-Identifier: GPL-2.0-only OR GPL-3.0-only

from amaranth import *
from amaranth.lib import wiring
from amaranth.lib.wiring import In, Out, Component

from memport import MemPortSource

class Frontend(Component):
	instruction: Out(32)
	address: Out(64)
	valid: Out(1)
	ready: In(1)

	def __init__(self):
		self.icache_refill = MemPortSource(64, 512)
		super().__init__()

	def elaborate(self, platform):
		m = Module()

		# Unpipelined fetch logic, which is just a simple state
		# machine that latches into both the PC and the IR.
		pc = Signal(64, init=0x20000000)
		ir = Signal(512)

		with m.FSM():
			with m.State("Request Fetch"):
				m.d.comb += [
					self.icache_refill.req.addr.eq(pc),
					self.icache_refill.req.valid.eq(1),
				]

				with m.If(self.icache_refill.req.ready):
					m.next = "Wait on Fetch Response"

			with m.State("Wait on Fetch Response"):
				m.d.comb += self.icache_refill.res.ready.eq(1)
				with m.If(self.icache_refill.res.valid):
					m.d.sync += [
						ir.eq(self.icache_refill.res.data),
					]
					m.next = "Decode Instructions"

			with m.State("Decode Instructions"):
				m.d.sync += pc.eq(pc + 4)
				m.d.comb += [
					self.valid.eq(1),
					self.instruction.eq(ir >> (pc % 512)),
				]
				with m.If((pc % 64) == 60):
					m.next = "Request Fetch"

		return m
