"""
Benchmark comparing pure SICP Agenda vs SimPy-backed Agenda.

Constructs multi-bit wide ripple-carry adders (32-bit, 64-bit, 128-bit) and simulates
multiple randomized vector additions to measure and compare throughput and execution time.
"""

import random
import sys
import time
from pathlib import Path

# Add project root to Python search path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from circuit_sim import (
    make_agenda,
    make_bus,
    make_simpy_agenda,
    make_wire,
    propagate,
    ripple_carry_adder,
    set_bus_values,
    set_signal,
)


def run_benchmark(width: int = 64, num_additions: int = 20):
    print(f"\n--- Benchmarking {width}-Bit Ripple-Carry Adder ({num_additions} Additions) ---")
    random.seed(42)
    test_vectors = [
        (random.randint(0, (1 << width) - 1), random.randint(0, (1 << width) - 1))
        for _ in range(num_additions)
    ]

    # 1. Pure SICP Agenda Benchmark
    t0 = time.perf_counter()
    for a_val, b_val in test_vectors:
        agenda = make_agenda()
        a_bus = make_bus(width, "A")
        b_bus = make_bus(width, "B")
        sum_bus = make_bus(width, "S")
        c_out = make_wire("c_out")
        ripple_carry_adder(a_bus, b_bus, sum_bus, c_out, agenda=agenda)
        set_bus_values(a_bus, a_val)
        set_bus_values(b_bus, b_val)
        propagate(agenda)
    sicp_time = time.perf_counter() - t0

    # 2. SimPy-backed Agenda Benchmark
    t0 = time.perf_counter()
    for a_val, b_val in test_vectors:
        agenda = make_simpy_agenda()
        a_bus = make_bus(width, "A")
        b_bus = make_bus(width, "B")
        sum_bus = make_bus(width, "S")
        c_out = make_wire("c_out")
        ripple_carry_adder(a_bus, b_bus, sum_bus, c_out, agenda=agenda)
        set_bus_values(a_bus, a_val)
        set_bus_values(b_bus, b_val)
        agenda.propagate()
    simpy_time = time.perf_counter() - t0

    print(f"  Pure SICP Agenda Time : {sicp_time * 1000:.2f} ms")
    print(f"  SimPy-backed Agenda   : {simpy_time * 1000:.2f} ms")
    speedup = (sicp_time / simpy_time) if simpy_time > 0 else 1.0
    print(f"  SimPy Efficiency      : {speedup:.2f}x relative execution rate")


def main():
    print("=" * 65)
    print("SICP vs SimPy Discrete-Event Engine Performance Benchmark")
    print("=" * 65)

    run_benchmark(width=16, num_additions=20)
    run_benchmark(width=32, num_additions=20)
    run_benchmark(width=64, num_additions=20)

    print("\n" + "=" * 65)


if __name__ == "__main__":
    main()
