# SPDX-License-Identifier: GPL-2.0-only OR GPL-3.0-only

from amaranth import *
from amaranth.lib import data
from amaranth.lib.wiring import Component, In, Out

from memport import MemPortSignature

class Buffer:
	def __init__(self, m, unbuffered, buffered):
		self.unbuffered = unbuffered
		self.buffered = buffered

		m.d.sync += [
			self.unbuffered.req.addr.eq(self.buffered.req.addr),
			self.buffered.req.ready.eq(self.unbuffered.req.ready),
			self.unbuffered.req.valid.eq(self.buffered.req.valid),
			self.buffered.res.data.eq(self.unbuffered.res.data),
			self.unbuffered.res.ready.eq(self.buffered.res.ready),
			self.buffered.res.valid.eq(self.unbuffered.res.valid),
		]
