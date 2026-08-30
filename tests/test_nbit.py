"""Tests for n-bit datapath primitives (bitwise ops, mux, register, ALU)."""

import pytest
from circuit_sim.agenda import make_agenda, propagate
from circuit_sim.nbit import (
    alu,
    bus_to_int,
    n_bit_and,
    n_bit_mux,
    n_bit_not,
    n_bit_or,
    n_bit_register,
    n_bit_xor,
    or_reduce,
)
from circuit_sim.sequential import sr_latch
from circuit_sim.wire import get_signal, make_bus, make_wire, set_bus_values, set_signal


def _clock_pulse(agenda, clk) -> None:
    """Issue a 0 -> 1 -> 0 pulse, propagating after each edge."""
    set_signal(clk, 0)
    propagate(agenda)
    set_signal(clk, 1)
    propagate(agenda)
    set_signal(clk, 0)
    propagate(agenda)


def test_n_bit_not_and_or_xor():
    agenda = make_agenda()
    a = make_bus(4, "A")
    b = make_bus(4, "B")
    not_out = make_bus(4, "N")
    and_out = make_bus(4, "AND")
    or_out = make_bus(4, "OR")
    xor_out = make_bus(4, "XOR")

    n_bit_not(a, not_out, agenda=agenda)
    n_bit_and(a, b, and_out, agenda=agenda)
    n_bit_or(a, b, or_out, agenda=agenda)
    n_bit_xor(a, b, xor_out, agenda=agenda)

    set_bus_values(a, 0b1010)
    set_bus_values(b, 0b1100)
    propagate(agenda)

    assert bus_to_int(not_out) == 0b0101
    assert bus_to_int(and_out) == 0b1000
    assert bus_to_int(or_out) == 0b1110
    assert bus_to_int(xor_out) == 0b0110


def test_n_bit_mux():
    agenda = make_agenda()
    a = make_bus(8, "A")
    b = make_bus(8, "B")
    out = make_bus(8, "O")
    sel = make_wire("sel")
    n_bit_mux(a, b, sel, out, agenda=agenda)

    set_bus_values(a, 42)
    set_bus_values(b, 99)
    set_signal(sel, 0)
    propagate(agenda)
    assert bus_to_int(out) == 42

    set_signal(sel, 1)
    propagate(agenda)
    assert bus_to_int(out) == 99


def test_or_reduce_and_width_mismatch():
    agenda = make_agenda()
    bus = make_bus(4, "B")
    out = make_wire("any")
    or_reduce(bus, out, agenda=agenda)

    set_bus_values(bus, 0)
    propagate(agenda)
    assert get_signal(out) == 0

    set_bus_values(bus, 0b0100)
    propagate(agenda)
    assert get_signal(out) == 1

    with pytest.raises(ValueError, match="width mismatch"):
        n_bit_and(make_bus(2, "x"), make_bus(3, "y"), make_bus(2, "z"), agenda=make_agenda())


def _alu_eval(width, x_val, y_val, zx_v, nx_v, zy_v, ny_v, f_v, no_v):
    agenda = make_agenda()
    x = make_bus(width, "X")
    y = make_bus(width, "Y")
    out = make_bus(width, "OUT")
    zx, nx, zy, ny, f, no = [make_wire(n) for n in ("zx", "nx", "zy", "ny", "f", "no")]
    zr = make_wire("zr")
    ng = make_wire("ng")
    alu(x, y, out, zx, nx, zy, ny, f, no, zr, ng, agenda=agenda)
    set_bus_values(x, x_val)
    set_bus_values(y, y_val)
    set_signal(zx, zx_v)
    set_signal(nx, nx_v)
    set_signal(zy, zy_v)
    set_signal(ny, ny_v)
    set_signal(f, f_v)
    set_signal(no, no_v)
    propagate(agenda)
    mask = (1 << width) - 1
    return bus_to_int(out) & mask, get_signal(zr), get_signal(ng)


def test_alu_nand2tetris_operations():
    """Classic Hack ALU functions on 8-bit buses."""
    width = 8
    x, y = 0b00001111, 0b00110011
    mask = (1 << width) - 1

    # 0: zx nx zy ny f no = 1 0 1 0 1 0
    out, zr, ng = _alu_eval(width, x, y, 1, 0, 1, 0, 1, 0)
    assert out == 0
    assert zr == 1
    assert ng == 0

    # 1: 1 1 1 1 1 1  -> 0+0 inverted then... Nand2Tetris: zx=1,nx=1,zy=1,ny=1,f=1,no=1 => 1
    out, zr, ng = _alu_eval(width, x, y, 1, 1, 1, 1, 1, 1)
    assert out == 1
    assert zr == 0

    # -1: 1 1 1 0 1 0
    out, _, ng = _alu_eval(width, x, y, 1, 1, 1, 0, 1, 0)
    assert out == mask
    assert ng == 1

    # x: 0 0 1 0 1 0
    out, _, _ = _alu_eval(width, x, y, 0, 0, 1, 0, 1, 0)
    assert out == x

    # y: 1 0 0 0 1 0
    out, _, _ = _alu_eval(width, x, y, 1, 0, 0, 0, 1, 0)
    assert out == y

    # !x: 0 0 1 0 1 1
    out, _, _ = _alu_eval(width, x, y, 0, 0, 1, 0, 1, 1)
    assert out == (~x) & mask

    # x+y: 0 0 0 0 1 0
    out, zr, ng = _alu_eval(width, x, y, 0, 0, 0, 0, 1, 0)
    assert out == (x + y) & mask
    assert zr == 0
    assert ng == 0

    # x&y: 0 0 0 0 0 0
    out, _, _ = _alu_eval(width, x, y, 0, 0, 0, 0, 0, 0)
    assert out == (x & y)

    # x-y: 0 1 0 0 1 1  (nx=1, f=1, no=1)
    out, _, _ = _alu_eval(width, x, y, 0, 1, 0, 0, 1, 1)
    assert out == (x - y) & mask


def test_n_bit_register_load_and_hold():
    agenda = make_agenda()
    d = make_bus(4, "D")
    q = make_bus(4, "Q")
    clk = make_wire("CLK")
    load = make_wire("LOAD")
    n_bit_register(d, clk, q, load=load, agenda=agenda)

    set_bus_values(d, 0b1010)
    set_signal(load, 1)
    _clock_pulse(agenda, clk)
    assert bus_to_int(q) == 0b1010

    set_bus_values(d, 0b0101)
    set_signal(load, 0)
    _clock_pulse(agenda, clk)
    assert bus_to_int(q) == 0b1010

    set_signal(load, 1)
    _clock_pulse(agenda, clk)
    assert bus_to_int(q) == 0b0101


def test_sr_latch_power_on_does_not_oscillate():
    agenda = make_agenda()
    s = make_wire("S")
    r = make_wire("R")
    q = make_wire("Q")
    q_bar = make_wire("Q_bar")
    sr_latch(s, r, q, q_bar, agenda=agenda)
    propagate(agenda)
    assert agenda.is_empty() is True
    assert get_signal(q) == 0
    assert get_signal(q_bar) == 1
