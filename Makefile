.SECONDARY:

check: $(patsubst tests/%.s,check/%.vcd,$(wildcard tests/*.s))
	@echo $^

# Cleanup
clean:
	rm -rf obj check

# Top-level verilog
obj/venv/stamp: \
		$(shell find tools/amaranth -type f) \
		$(shell find tools/pyelftools -type f)
	rm -rf $(dir $@)
	mkdir -p $(dir $@)
	python -m venv $(abspath $(dir $@))
	obj/venv/bin/pip install tools/amaranth
	obj/venv/bin/pip install tools/pyelftools
	date > $@

obj/tests/%.elf: tests/%.s tests/test.ld
	mkdir -p $(dir $@)
	riscv64-linux-gnu-gcc -march=rv64i -mabi=lp64 $< -o $@ -T$(filter %.ld,$^) -nostdlib -nostartfiles

check/%.vcd: rtl/top.py obj/tests/%.elf $(shell find rtl/ -type f) obj/venv/stamp
	mkdir -p $(dir $@)
	obj/venv/bin/python $< --output-vcd $@ --bootrom-elf $(filter %.elf,$^)
	touch -c $@
