OUTPUT_FORMAT("elf64-littleriscv", "elf64-littleriscv",
              "elf64-littleriscv")
OUTPUT_ARCH(riscv)
ENTRY(_start)

MEMORY
{
  bootrom (irx!wa) : ORIGIN = 0x20000000, LENGTH = 0x4000
}

PHDRS
{
  bootrom PT_LOAD;
}

SECTIONS
{
  .text : {
    *(.text)
  } >bootrom :bootrom
}
