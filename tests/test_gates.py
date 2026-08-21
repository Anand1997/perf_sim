"""Tests for primitive logic gates and boolean functions."""

import pytest
from circuit_sim.agenda import current_time, make_agenda, propagate
from circuit_sim.gates import (
    AndGate,
    Inverter,
    NandGate,
    NorGate,
    OrGate,
    XorGate,
    and_gate,
    compound_or_gate,
    inverter,
    logical_and,
    logical_nand,
    logical_nor,
    logical_not,
    logical_or,
    logical_xor,
    nand_gate,
    nor_gate,
    or_gate,
    xor_gate,
)
from circuit_sim.wire import get_signal, make_wire, set_signal


def test_pure_logic_functions():
    assert logical_not(0) == 1
    assert logical_not(1) == 0
    with pytest.raises(ValueError):
        logical_not(2)

    assert logical_and(0, 0) == 0
    assert logical_and(0, 1) == 0
    assert logical_and(1, 0) == 0
    assert logical_and(1, 1) == 1

    assert logical_or(0, 0) == 0
    assert logical_or(0, 1) == 1
    assert logical_or(1, 0) == 1
    assert logical_or(1, 1) == 1

    assert logical_nand(1, 1) == 0
    assert logical_nand(1, 0) == 1
    assert logical_nor(0, 0) == 1
    assert logical_nor(0, 1) == 0
    assert logical_xor(0, 1) == 1
    assert logical_xor(1, 1) == 0


def test_inverter_gate():
    agenda = make_agenda()
    in_w = make_wire("in")
    out_w = make_wire("out")

    inverter(in_w, out_w, delay=2, agenda=agenda)
    # At registration (in_w=0), out_w scheduled to become 1 at t=2
    assert get_signal(out_w) == 0
    propagate(agenda)
    assert get_signal(out_w) == 1
    assert current_time(agenda) == 2

    # Change in_w to 1
    set_signal(in_w, 1)
    propagate(agenda)
    assert get_signal(out_w) == 0
    assert current_time(agenda) == 4


def test_and_gate():
    agenda = make_agenda()
    a = make_wire("a")
    b = make_wire("b")
    out = make_wire("out")

    and_gate(a, b, out, delay=3, agenda=agenda)
    propagate(agenda)
    assert get_signal(out) == 0

    # a=1, b=0 -> out=0
    set_signal(a, 1)
    propagate(agenda)
    assert get_signal(out) == 0

    # a=1, b=1 -> out=1 at t = current_time + 3
    t_before = current_time(agenda)
    set_signal(b, 1)
    propagate(agenda)
    assert get_signal(out) == 1
    assert current_time(agenda) == t_before + 3


def test_or_gate():
    agenda = make_agenda()
    a = make_wire("a")
    b = make_wire("b")
    out = make_wire("out")

    or_gate(a, b, out, delay=5, agenda=agenda)
    propagate(agenda)
    assert get_signal(out) == 0

    t_before = current_time(agenda)
    set_signal(a, 1)
    propagate(agenda)
    assert get_signal(out) == 1
    assert current_time(agenda) == t_before + 5


def test_compound_or_gate_demorgan():
    agenda = make_agenda()
    a = make_wire("a")
    b = make_wire("b")
    out = make_wire("out")

    compound_or_gate(a, b, out, agenda=agenda)
    propagate(agenda)
    assert get_signal(out) == 0

    # Set a=1
    set_signal(a, 1)
    propagate(agenda)
    assert get_signal(out) == 1


def test_nand_nor_xor_gates():
    agenda = make_agenda()
    a = make_wire("a")
    b = make_wire("b")
    out_nand = make_wire("nand")
    out_nor = make_wire("nor")
    out_xor = make_wire("xor")

    nand_gate(a, b, out_nand, delay=3, agenda=agenda)
    nor_gate(a, b, out_nor, delay=5, agenda=agenda)
    xor_gate(a, b, out_xor, delay=8, agenda=agenda)

    propagate(agenda)
    # Initially a=0, b=0
    assert get_signal(out_nand) == 1
    assert get_signal(out_nor) == 1
    assert get_signal(out_xor) == 0

    # a=1, b=0
    set_signal(a, 1)
    propagate(agenda)
    assert get_signal(out_nand) == 1
    assert get_signal(out_nor) == 0
    assert get_signal(out_xor) == 1

    # a=1, b=1
    set_signal(b, 1)
    propagate(agenda)
    assert get_signal(out_nand) == 0
    assert get_signal(out_nor) == 0
    assert get_signal(out_xor) == 0


def test_class_syntax_instantiation():
    agenda = make_agenda()
    w1 = make_wire()
    w2 = make_wire()
    out = make_wire()

    g = AndGate(w1, w2, out, delay=3, agenda=agenda)
    assert repr(g).startswith("AndGate")
    set_signal(w1, 1)
    set_signal(w2, 1)
    propagate(agenda)
    assert get_signal(out) == 1
