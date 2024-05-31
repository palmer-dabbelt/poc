# SPDX-License-Identifier: GPL-2.0-only OR GPL-3.0-only

from amaranth import *
from amaranth.lib import data
from amaranth.lib.wiring import Signature, In, Out, connect, flipped

class MemPortReqSignature(Signature):
	def __init__(self, address_bits):
		super().__init__({
			"addr": Out(address_bits),
			"ready": In(1),
			"valid": Out(1),
		})

class MemPortResSignature(Signature):
	def __init__(self, data_bits):
		super().__init__({
			"data": In(data_bits),
			"ready": Out(1),
			"valid": In(1),
		})

class MemPortSource(Elaboratable):
	def __init__(self, address_bits, data_bits):
		self.req = MemPortReqSignature(address_bits).create()
		self.res = MemPortResSignature(data_bits).create()

	def connect(self, m, that):
		connect(m, self.req, flipped(that.req))
