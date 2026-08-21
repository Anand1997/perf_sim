"""
Half-Adder Demo from SICP Section 3.3.4.

This example mirrors the exact sequence from the SICP textbook:
1. Initialize agenda and wires (input-1, input-2, sum, carry).
2. Attach probes to sum and carry wires.
3. Construct the half-adder circuit connecting the wires.
4. Set input-1 to 1 and call propagate() -> sum changes to 1 at t=8.
5. Set input-2 to 1 and call propagate() -> carry changes to 1 at t=11, sum changes to 0 at t=16.
"""

import os
import sys
from pathlib import Path

# Add project root to Python search path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from circuit_sim import (
    current_time,
    half_adder,
    make_agenda,
    make_wire,
    probe,
    propagate,
    set_signal,
)


def main():
    print("=" * 60)
    print("SICP Section 3.3.4: Half-Adder Simulation Walkthrough")
    print("=" * 60)

    # 1. Initialize agenda and wires
    the_agenda = make_agenda()
    input_1 = make_wire("input-1")
    input_2 = make_wire("input-2")
    sum_wire = make_wire("sum")
    carry_wire = make_wire("carry")

    # 2. Attach probes
    print("\n[Step 1] Attaching Probes to 'sum' and 'carry':")
    probe("sum", sum_wire, agenda=the_agenda)
    probe("carry", carry_wire, agenda=the_agenda)

    # 3. Construct the half-adder
    print("\n[Step 2] Constructing Half-Adder...")
    half_adder(input_1, input_2, sum_wire, carry_wire, agenda=the_agenda)

    # 4. Set input-1 to 1
    print("\n[Step 3] Setting input-1 to 1 and running propagate():")
    set_signal(input_1, 1)
    propagate(the_agenda)
    print(f"Simulation completed at current-time = {current_time(the_agenda)}")

    # 5. Set input-2 to 1
    print("\n[Step 4] Setting input-2 to 1 and running propagate():")
    set_signal(input_2, 1)
    propagate(the_agenda)
    print(f"Simulation completed at current-time = {current_time(the_agenda)}")
    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
