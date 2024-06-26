# SPDX-License-Identifier: GPL-2.0-only OR GPL-3.0-only

from amaranth import *
from amaranth.lib import wiring
from amaranth.lib.wiring import In, Out
from amaranth.sim import *

from core import Core, CoreRunState

from elftools.elf.elffile import ELFFile

import argparse
from argparse import ArgumentParser

parser = ArgumentParser()
parser.add_argument("--output-vcd", type=argparse.FileType('w'), required=True)
parser.add_argument("--bootrom-elf", required=True)
args = parser.parse_args()

class TestBenchMemory:
	def __init__(self, elf):
		self.elf = elf

	def readb(self, addr):
		for section in self.elf.iter_sections():
			sh_base = section['sh_addr']
			sh_limit = sh_base + len(section.data())
			if (addr >= sh_base and addr < sh_limit):
				return section.data()[addr - sh_base]

		raise Exception("Unknown Address")

	def readh(self, addr):
		return self.readb(addr) + (self.readb(addr + 1) << 8)

tb_mem = TestBenchMemory(ELFFile(open(args.bootrom_elf, "rb")))
tb_mem.readb(0x20000000)

dut = Core()
def bench():
	for _ in range(300):
		yield dut.memport.req.ready.eq(1)
		valid = yield dut.memport.req.valid
		if valid:
			addr = yield dut.memport.req.addr
			data = 0
			count = 0
			for x in range(62, -2, -2):
				try:
					data = tb_mem.readh(addr + x) | (data << 16)
					count = count + 1
				except:
					data = (data << 16)
			yield Tick()
			yield dut.memport.res.data.eq(data)
			yield dut.memport.res.valid.eq(1)
			yield dut.valid_bytes.eq(count * 2)
			yield Tick()
			while (yield dut.memport.res.ready != 1):
				yield Tick()
			yield dut.memport.res.valid.eq(0)
			yield Tick()
		yield Tick()

	assert (yield dut.state == CoreRunState.SUCCESS)

sim = Simulator(dut)
sim.add_clock(1e-6) # 1 MHz
sim.add_testbench(bench)
with sim.write_vcd(args.output_vcd):
	sim.run()
