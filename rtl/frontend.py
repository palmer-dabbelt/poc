# SPDX-License-Identifier: GPL-2.0-only OR GPL-3.0-only

from amaranth import *
from amaranth.lib import wiring
from amaranth.lib.wiring import In, Out, Component

class Frontend(Component):
	instruction: Out(32)
	address: Out(32)
	valid: Out(1)
	ready: In(1)

	def __init(self):
		super.__init__()

	def elaborate(self, platform):
		m = Module()


		with m.If(self.address == 0x00000010):
			m.d.comb += self.instruction.eq(0x0000007f)
		with m.Else():
			m.d.comb += self.instruction.eq(0)

		m.d.comb += self.valid.eq(1)
		m.d.sync += self.address.eq(self.address + 4)

		return m
