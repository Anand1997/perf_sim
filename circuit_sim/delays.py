"""
Gate delays configuration for the SICP Digital Circuit Simulator.

In SICP Section 3.3.4, primitive gates operate with specific propagation delays:
- Inverter delay: 2 units
- AND gate delay: 3 units
- OR gate delay: 5 units
"""

from typing import NamedTuple


class Delays(NamedTuple):
    """Immutable record storing propagation delays for digital logic gates."""
    inverter: int = 2
    and_gate: int = 3
    or_gate: int = 5
    nand_gate: int = 3
    nor_gate: int = 5
    xor_gate: int = 8


# Standard default delays specified in SICP 3.3.4
DEFAULT_DELAYS = Delays(
    inverter=2,
    and_gate=3,
    or_gate=5,
    nand_gate=3,
    nor_gate=5,
    xor_gate=8,
)
