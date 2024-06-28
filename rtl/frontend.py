# SPDX-License-Identifier: GPL-2.0-only OR GPL-3.0-only

from amaranth import *
from amaranth.lib import wiring
from amaranth.lib.wiring import In, Out, Component

from memport import MemPortSignature

# The fetch unit provides cache lines of instruction-flavored data to the
# pipeline, by asking for cache lines from the memory system.
class Fetch(Component):
	def __init__(self):
		super().__init__({
			"req_addr": In(64),
			"req_valid": In(1),
			"req_ready": Out(1),

			"res_data": Out(512),
			"res_addr": Out(64),
			"res_valid": Out(1),
			"res_ready": In(1),

			"icache_refill": Out(MemPortSignature(64, 512))
		})

	def elaborate(self, platform):
		m = Module()

		# Technically it's a cache...
		cache_addr = Signal(64)
		cache_line = Signal(512)

		with m.FSM():
			with m.State("Wait on Instruction Request"):
				m.d.comb += self.req_ready.eq(1)
				m.d.sync += cache_addr.eq(self.req_addr)
				with m.If(self.req_valid):
					m.next = "Request ICache Refill"

			with m.State("Request ICache Refill"):
				m.d.comb += [
					self.icache_refill.req.addr.eq(cache_addr),
					self.icache_refill.req.valid.eq(1),
				]

				with m.If(self.icache_refill.req.ready):
					m.next = "Wait on ICache Refill"

			with m.State("Wait on ICache Refill"):
				m.d.comb += self.icache_refill.res.ready.eq(1)
				with m.If(self.icache_refill.res.valid):
					m.d.sync += [
						cache_line.eq(self.icache_refill.res.data),
					]
					m.next = "Provide Instruction Response"

			with m.State("Provide Instruction Response"):
				m.d.comb += [
					self.res_data.eq(cache_line),
					self.res_addr.eq(cache_addr),
					self.res_valid.eq(1),
				]

				with m.If(self.res_ready):
					m.next = "Wait on Instruction Request"

		return m

class Decode(Component):
	line_req_addr: Out(64)
	line_req_valid: Out(1)
	line_req_ready: In(1)

	line_res_data: In(512)
	line_res_addr: In(64)
	line_res_valid: In(1)
	line_res_ready: Out(1)

	insn_data: Out(32)
	insn_addr: Out(64)
	insn_valid: Out(1)
	insn_ready: In(1)

	def __init__(self):
		super().__init__()

	def elaborate(self, platform):
		m = Module()

		# This is just scalar decode for now, no reason to make things
		# more complicated than they need to be.  So all we really need
		# to do is just step through the instructions in a cache line.
		pc = Signal(64, init=0x20000000)
		ir = Signal(512)

		with m.FSM():
			with m.State("Request Line"):
				m.d.comb += [
					self.line_req_addr.eq(pc),
					self.line_req_valid.eq(1),
				]
				with m.If(self.line_req_ready):
					m.next = "Wait on Line"

			with m.State("Wait on Line"):
				m.d.sync += [
					ir.eq(self.line_res_data),
					pc.eq(self.line_res_addr),
				]
				m.d.comb += self.line_res_ready.eq(1)
				with m.If(self.line_res_valid):
					m.next = "Provide Instructions"

			with m.State("Provide Instructions"):
				m.d.comb += [
					self.insn_valid.eq(1),
					self.insn_data.eq(ir >> ((pc % 64) * 8)),
					self.insn_addr.eq(pc),
				]
				with m.If(self.insn_ready):
					m.d.sync += pc.eq(pc + 4)
					with m.If((pc % 64) == 60):
						m.next = "Request Line"

		return m

class Frontend(Component):
	def __init__(self):
		super().__init__({
			"instruction": Out(32),
			"address": Out(64),
			"valid": Out(1),
			"ready": In(1),
			"icache_refill": Out(MemPortSignature(64, 512))
		})

	def elaborate(self, platform):
		m = Module()

		m.submodules.fetch = fetch = Fetch()
		m.submodules.decode = decode = Decode()

		m.d.comb += [
			fetch.icache_refill.req.ready.eq(self.icache_refill.req.ready),
			self.icache_refill.req.valid.eq(fetch.icache_refill.req.valid),
			self.icache_refill.req.addr.eq(fetch.icache_refill.req.addr),
			self.icache_refill.res.ready.eq(fetch.icache_refill.res.ready),
			fetch.icache_refill.res.valid.eq(self.icache_refill.res.valid),
			fetch.icache_refill.res.data.eq(self.icache_refill.res.data),
		]

		m.d.comb += [
			fetch.req_addr.eq(decode.line_req_addr),
			fetch.req_valid.eq(decode.line_req_valid),
			decode.line_req_ready.eq(fetch.req_ready),
			decode.line_res_data.eq(fetch.res_data),
			decode.line_res_addr.eq(fetch.res_addr),
			decode.line_res_valid.eq(fetch.res_valid),
			fetch.res_ready.eq(decode.line_res_ready),
		]

		m.d.comb += [
			self.instruction.eq(decode.insn_data),
			self.address.eq(decode.insn_addr),
			self.valid.eq(decode.insn_valid),
			decode.insn_ready.eq(self.ready),
		]

		return m
