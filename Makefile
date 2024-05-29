check: up_counter.vcd

# Cleanup
clean:
	rm -rf obj

# Top-level verilog
obj/venv/stamp: $(shell find tools/amaranth -type f)
	rm -rf $(dir $@)
	mkdir -p $(dir $@)
	python -m venv $(abspath $(dir $@))
	obj/venv/bin/pip install tools/amaranth
	date > $@

up_counter.vcd: rtl/top.py $(shell find rtl/ -type f) obj/venv/stamp
	mkdir -p $(dir $@)
	obj/venv/bin/python $< -o $@
	touch -c $@
