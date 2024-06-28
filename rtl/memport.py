# SPDX-License-Identifier: GPL-2.0-only OR GPL-3.0-only

from amaranth import *
from amaranth.lib import data
from amaranth.lib.wiring import Signature, In, Out, PureInterface

class MemPortReqSignature(Signature):
	def __init__(self, address_bits):
		self.address_bits = address_bits
		super().__init__({
			"addr": Out(address_bits),
			"ready": In(1),
			"valid": Out(1),
		})

	def __eq__(self, other):
		return isinstance(other, MemPortReqSignature) and self.address_bits == other.address_bits

	def __repr__(self):
		return f"MemPortReqSignature({self.address_bits})"

	def create(self, *, path=None, src_loc_at=0):
		return MemPortReqInterface(self, path=path, src_loc_at=1 + src_loc_at)

class MemPortReqInterface(PureInterface):
	pass

class MemPortResSignature(Signature):
	def __init__(self, data_bits):
		self.data_bits = data_bits
		super().__init__({
			"data": In(data_bits),
			"ready": Out(1),
			"valid": In(1),
		})

	def __eq__(self, other):
		return isinstance(other, MemPortResSignature) and self.data_bits == other.data_bits

	def __repr__(self):
		return f"MemPortResSignature({self.data_bits})"

	def create(self, *, path=None, src_loc_at=0):
		return MemPortResInterface(self, path=path, src_loc_at=1 + src_loc_at)

class MemPortResInterface(PureInterface):
	pass

class MemPortSignature(Signature):
	def __init__(self, address_bits, data_bits):
		self.address_bits = address_bits
		self.data_bits = data_bits
		super().__init__({
			"req": Out(MemPortReqSignature(address_bits)),
			"res": In(MemPortResSignature(data_bits)),
		})

	def __eq__(self, other):
		return isinstance(other, MemPortSignature) and self.members == other.members

	def __repr__(self):
		return f"MemPortSignature({self.address_bits}, {self.data_bits})"

	def create(self, *, path=None, src_loc_at=0):
		return MemPortInterface(self, path=path, src_loc_at=1 + src_loc_at)

class MemPortInterface(PureInterface):
	pass
