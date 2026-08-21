"""
Full-Adder Demo with Truth Table Verification.

Demonstrates the 1-bit full-adder circuit built from two half-adders and an OR gate.
Runs through all 8 combinations of (A, B, Carry-In) and monitors transitions.
"""

import sys
from pathlib import Path

# Add project root to Python search path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from circuit_sim import (
    current_time,
    full_adder,
    get_signal,
    make_agenda,
    make_wire,
    probe,
    propagate,
    set_signal,
)


def main():
    print("=" * 60)
    print("Full-Adder Circuit Simulation")
    print("=" * 60)
    print(f"{'A':^5} | {'B':^5} | {'Cin':^5} | {'Sum':^5} | {'Cout':^5} | {'Sim Time':^10}")
    print("-" * 60)

    for a_val in (0, 1):
        for b_val in (0, 1):
            for cin_val in (0, 1):
                agenda = make_agenda()
                a = make_wire("A")
                b = make_wire("B")
                cin = make_wire("Cin")
                sum_wire = make_wire("Sum")
                cout_wire = make_wire("Cout")

                full_adder(a, b, cin, sum_wire, cout_wire, agenda=agenda)
                set_signal(a, a_val)
                set_signal(b, b_val)
                set_signal(cin, cin_val)
                propagate(agenda)

                s = get_signal(sum_wire)
                co = get_signal(cout_wire)
                t = current_time(agenda)
                print(f"{a_val:^5} | {b_val:^5} | {cin_val:^5} | {s:^5} | {co:^5} | {t:^10}")

    print("=" * 60)


if __name__ == "__main__":
    main()
