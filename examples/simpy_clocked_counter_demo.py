"""
SimPy Clocked Sequential Circuit Demo.

Demonstrates a clock generator process driving sequential digital logic (D Flip-Flop)
in a SimPy-powered discrete-event environment.
"""

import sys
from pathlib import Path

# Add project root to Python search path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from circuit_sim import (
    clock_generator,
    d_flip_flop,
    get_signal,
    make_simpy_agenda,
    make_wire,
    probe,
    pulse_generator,
)


def main():
    print("=" * 65)
    print("SimPy Clocked Circuit: Positive-Edge-Triggered D Flip-Flop")
    print("=" * 65)

    agenda = make_simpy_agenda()
    clk = make_wire("CLK")
    d = make_wire("D")
    q = make_wire("Q")
    q_bar = make_wire("Q_BAR")

    # Monitor wires
    probe("CLK", clk, agenda=agenda)
    probe("D  ", d, agenda=agenda)
    probe("Q  ", q, agenda=agenda)

    # Build edge-triggered D flip-flop
    d_flip_flop(d, clk, q, q_bar, agenda=agenda)

    # 1. Spawn periodic clock (10 units high, 10 units low = period of 20)
    print("\n[Starting Clock Generator (Period=20)]")
    clock_generator(agenda, clk, high_duration=10, low_duration=10, cycles=5)

    # 2. Drive D with a pulse sequence: D goes high at t=15 (before rising edge at t=20),
    # then low at t=35 (before rising edge at t=40)
    print("[Starting Data Stimulus Generator]")
    pulse_generator(agenda, d, sequence=[(15, 0), (20, 1), (25, 0)])

    print("\n[Running SimPy Simulation...]")
    agenda.propagate()

    print(f"\nFinal State at t={agenda.get_current_time()}: Q={get_signal(q)}, Q_BAR={get_signal(q_bar)}")
    print("=" * 65)


if __name__ == "__main__":
    main()
