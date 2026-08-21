"""
Ripple-Carry Adder Demo (SICP Exercise 3.30).

Simulates an 8-bit ripple-carry adder computing various binary additions:
- 42 + 27 = 69
- 127 + 129 = 256 (overflow carry-out)
"""

import sys
from pathlib import Path

# Add project root to Python search path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from circuit_sim import (
    current_time,
    get_bus_values,
    get_signal,
    make_agenda,
    make_bus,
    make_wire,
    propagate,
    ripple_carry_adder,
    set_bus_values,
    set_signal,
)


def bits_to_int(bits):
    return sum(bit << i for i, bit in enumerate(bits))


def run_addition(num_a: int, num_b: int, width: int = 8, cin_val: int = 0):
    agenda = make_agenda()
    a_bus = make_bus(width, "A")
    b_bus = make_bus(width, "B")
    sum_bus = make_bus(width, "Sum")
    c_out = make_wire("Cout")
    c_in = make_wire("Cin")

    ripple_carry_adder(a_bus, b_bus, sum_bus, c_out, c_in=c_in, agenda=agenda)

    set_bus_values(a_bus, num_a)
    set_bus_values(b_bus, num_b)
    set_signal(c_in, cin_val)
    propagate(agenda)

    sum_bits = get_bus_values(sum_bus)
    cout_val = get_signal(c_out)
    total_val = bits_to_int(sum_bits) + (cout_val << width)

    print(f"Adding: {num_a} (0b{num_a:0{width}b}) + {num_b} (0b{num_b:0{width}b}) [Cin={cin_val}]")
    print(f"  Sum bits (LSB->MSB) : {sum_bits}")
    print(f"  Carry-Out           : {cout_val}")
    print(f"  Calculated Value    : {total_val} (Expected: {num_a + num_b + cin_val})")
    print(f"  Simulation Delay    : {current_time(agenda)} time units")
    print("-" * 60)


def main():
    print("=" * 60)
    print("SICP Exercise 3.30: 8-Bit Ripple-Carry Adder Demo")
    print("=" * 60)

    run_addition(42, 27, width=8, cin_val=0)
    run_addition(127, 129, width=8, cin_val=0)
    run_addition(255, 1, width=8, cin_val=0)
    run_addition(15, 15, width=8, cin_val=1)

    print("=" * 60)


if __name__ == "__main__":
    main()
