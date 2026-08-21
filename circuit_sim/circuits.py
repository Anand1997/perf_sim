"""
Compound Digital Circuits (SICP Section 3.3.4 & Exercises).

This module implements higher-level compound digital circuits by composing
primitive logic gates:
- Half-Adder
- Full-Adder
- Ripple-Carry Adder (Exercise 3.30)
- 2-to-1 Multiplexer
- 1-to-2 Demultiplexer
"""

from typing import Any, Callable, List, Optional, Sequence

from circuit_sim.delays import DEFAULT_DELAYS, Delays
from circuit_sim.gates import and_gate, inverter, or_gate
from circuit_sim.wire import make_wire


def half_adder(
    a: Callable[..., Any],
    b: Callable[..., Any],
    s: Callable[..., Any],
    c: Callable[..., Any],
    delays: Optional[Delays] = None,
    agenda: Optional[Callable[..., Any]] = None,
) -> str:
    """
    Constructs a Half-Adder circuit (SICP half-adder).
    
    Inputs:
        a, b: Input wires
    Outputs:
        s: Sum wire (a XOR b)
        c: Carry wire (a AND b)
        
    Internal architecture:
        d = a OR b
        c = a AND b
        e = NOT c
        s = d AND e
    """
    d_delays = delays or DEFAULT_DELAYS
    d = make_wire("ha_d")
    e = make_wire("ha_e")

    or_gate(a, b, d, delay=d_delays.or_gate, agenda=agenda)
    and_gate(a, b, c, delay=d_delays.and_gate, agenda=agenda)
    inverter(c, e, delay=d_delays.inverter, agenda=agenda)
    and_gate(d, e, s, delay=d_delays.and_gate, agenda=agenda)
    return "ok"


def full_adder(
    a: Callable[..., Any],
    b: Callable[..., Any],
    c_in: Callable[..., Any],
    sum_wire: Callable[..., Any],
    c_out: Callable[..., Any],
    delays: Optional[Delays] = None,
    agenda: Optional[Callable[..., Any]] = None,
) -> str:
    """
    Constructs a Full-Adder circuit (SICP full-adder).
    
    Inputs:
        a, b : Operand bits
        c_in : Carry-in bit
    Outputs:
        sum_wire : Resulting sum bit (a XOR b XOR c_in)
        c_out    : Resulting carry-out bit
        
    Composed of two half-adders and one OR gate:
        half_adder(b, c_in, s, c1)
        half_adder(a, s, sum_wire, c2)
        or_gate(c1, c2, c_out)
    """
    d_delays = delays or DEFAULT_DELAYS
    s = make_wire("fa_s")
    c1 = make_wire("fa_c1")
    c2 = make_wire("fa_c2")

    half_adder(b, c_in, s, c1, delays=d_delays, agenda=agenda)
    half_adder(a, s, sum_wire, c2, delays=d_delays, agenda=agenda)
    or_gate(c1, c2, c_out, delay=d_delays.or_gate, agenda=agenda)
    return "ok"


def ripple_carry_adder(
    a_wires: Sequence[Callable[..., Any]],
    b_wires: Sequence[Callable[..., Any]],
    sum_wires: Sequence[Callable[..., Any]],
    c_out: Callable[..., Any],
    c_in: Optional[Callable[..., Any]] = None,
    delays: Optional[Delays] = None,
    agenda: Optional[Callable[..., Any]] = None,
) -> str:
    """
    Constructs an n-bit Ripple-Carry Adder (SICP Exercise 3.30).
    
    Cascades n full-adders together. Input wires are arranged in order from
    index 0 (least significant bit, bit 0) to index n-1 (most significant bit).
    
    Args:
        a_wires   : List of n input wires for operand A (LSB first).
        b_wires   : List of n input wires for operand B (LSB first).
        sum_wires : List of n output wires for sum (LSB first).
        c_out     : Output wire for final carry-out bit.
        c_in      : Optional initial carry-in wire (defaults to 0).
        delays    : Gate delay configuration.
        agenda    : Simulation agenda.
        
    Total propagation delay:
        n * full_adder_delay
    """
    n = len(a_wires)
    if len(b_wires) != n or len(sum_wires) != n:
        raise ValueError(
            f"Bus width mismatch: a={len(a_wires)}, b={len(b_wires)}, sum={len(sum_wires)}"
        )
    if n == 0:
        raise ValueError("Ripple-carry adder requires at least 1 bit")

    d_delays = delays or DEFAULT_DELAYS
    current_c_in = c_in if c_in is not None else make_wire("rca_c_in_0")

    for i in range(n):
        # The last stage outputs to c_out, otherwise intermediate carry wire
        stage_c_out = c_out if i == n - 1 else make_wire(f"rca_carry_{i}")
        full_adder(
            a_wires[i],
            b_wires[i],
            current_c_in,
            sum_wires[i],
            stage_c_out,
            delays=d_delays,
            agenda=agenda,
        )
        current_c_in = stage_c_out

    return "ok"


def multiplexer(
    a: Callable[..., Any],
    b: Callable[..., Any],
    sel: Callable[..., Any],
    out_wire: Callable[..., Any],
    delays: Optional[Delays] = None,
    agenda: Optional[Callable[..., Any]] = None,
) -> str:
    """
    Constructs a 2-to-1 Multiplexer.
    
    When sel == 0, out_wire = a
    When sel == 1, out_wire = b
    
    Logic: out = (a AND NOT sel) OR (b AND sel)
    """
    d_delays = delays or DEFAULT_DELAYS
    not_sel = make_wire("mux_not_sel")
    term_a = make_wire("mux_term_a")
    term_b = make_wire("mux_term_b")

    inverter(sel, not_sel, delay=d_delays.inverter, agenda=agenda)
    and_gate(a, not_sel, term_a, delay=d_delays.and_gate, agenda=agenda)
    and_gate(b, sel, term_b, delay=d_delays.and_gate, agenda=agenda)
    or_gate(term_a, term_b, out_wire, delay=d_delays.or_gate, agenda=agenda)
    return "ok"


def demultiplexer(
    in_wire: Callable[..., Any],
    sel: Callable[..., Any],
    out_a: Callable[..., Any],
    out_b: Callable[..., Any],
    delays: Optional[Delays] = None,
    agenda: Optional[Callable[..., Any]] = None,
) -> str:
    """
    Constructs a 1-to-2 Demultiplexer.
    
    When sel == 0: out_a = in_wire, out_b = 0
    When sel == 1: out_a = 0,       out_b = in_wire
    """
    d_delays = delays or DEFAULT_DELAYS
    not_sel = make_wire("demux_not_sel")

    inverter(sel, not_sel, delay=d_delays.inverter, agenda=agenda)
    and_gate(in_wire, not_sel, out_a, delay=d_delays.and_gate, agenda=agenda)
    and_gate(in_wire, sel, out_b, delay=d_delays.and_gate, agenda=agenda)
    return "ok"
