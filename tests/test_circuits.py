"""Tests for compound digital circuits (half-adder, full-adder, ripple-carry adder, mux, demux)."""

import pytest
from circuit_sim.agenda import current_time, make_agenda, propagate
from circuit_sim.circuits import (
    demultiplexer,
    full_adder,
    half_adder,
    multiplexer,
    ripple_carry_adder,
)
from circuit_sim.delays import Delays
from circuit_sim.probe import make_probe_recorder, probe
from circuit_sim.wire import (
    get_bus_values,
    get_signal,
    make_bus,
    make_wire,
    set_bus_values,
    set_signal,
)


def test_half_adder_truth_table():
    """Verify half-adder logic for all 4 input combinations."""
    for a_val, b_val, expected_sum, expected_carry in [
        (0, 0, 0, 0),
        (0, 1, 1, 0),
        (1, 0, 1, 0),
        (1, 1, 0, 1),
    ]:
        agenda = make_agenda()
        a = make_wire("a")
        b = make_wire("b")
        s = make_wire("s")
        c = make_wire("c")

        half_adder(a, b, s, c, agenda=agenda)
        set_signal(a, a_val)
        set_signal(b, b_val)
        propagate(agenda)

        assert get_signal(s) == expected_sum, f"Failed sum for ({a_val}, {b_val})"
        assert get_signal(c) == expected_carry, f"Failed carry for ({a_val}, {b_val})"


def test_sicp_half_adder_timing_trace():
    """
    Exact simulation trace from SICP Section 3.3.4:
    - input-1 and input-2 initialized to 0
    - probe attached to sum and carry
    - input-1 set to 1 -> sum becomes 1 at time 8
    - input-2 set to 1 -> carry becomes 1 at time 11, sum becomes 0 at time 16
    """
    agenda = make_agenda()
    input_1 = make_wire("input-1")
    input_2 = make_wire("input-2")
    sum_wire = make_wire("sum")
    carry_wire = make_wire("carry")

    recorder = make_probe_recorder()
    probe("sum", sum_wire, agenda=agenda, callback=recorder.callback)
    probe("carry", carry_wire, agenda=agenda, callback=recorder.callback)

    half_adder(input_1, input_2, sum_wire, carry_wire, agenda=agenda)

    # Initial probe registration at t=0
    assert ("sum", 0, 0) in recorder.transitions
    assert ("carry", 0, 0) in recorder.transitions

    # Action 1: set input-1 to 1
    recorder.clear()
    set_signal(input_1, 1)
    propagate(agenda)

    # In SICP, sum becomes 1 at t=8
    assert recorder.transitions == [("sum", 8, 1)]
    assert get_signal(sum_wire) == 1
    assert get_signal(carry_wire) == 0

    # Action 2: set input-2 to 1
    recorder.clear()
    set_signal(input_2, 1)
    propagate(agenda)

    # In SICP:
    # carry 11 New-value = 1
    # sum 16 New-value = 0
    assert recorder.transitions == [
        ("carry", 11, 1),
        ("sum", 16, 0),
    ]
    assert get_signal(sum_wire) == 0
    assert get_signal(carry_wire) == 1


def test_full_adder_truth_table():
    """Test all 8 input combinations for full-adder."""
    for a_val in (0, 1):
        for b_val in (0, 1):
            for cin_val in (0, 1):
                total = a_val + b_val + cin_val
                expected_sum = total % 2
                expected_cout = total // 2

                agenda = make_agenda()
                a = make_wire("a")
                b = make_wire("b")
                cin = make_wire("cin")
                s = make_wire("s")
                cout = make_wire("cout")

                full_adder(a, b, cin, s, cout, agenda=agenda)
                set_signal(a, a_val)
                set_signal(b, b_val)
                set_signal(cin, cin_val)
                propagate(agenda)

                assert get_signal(s) == expected_sum, f"Failed sum for ({a_val}, {b_val}, {cin_val})"
                assert get_signal(cout) == expected_cout, f"Failed cout for ({a_val}, {b_val}, {cin_val})"


def test_ripple_carry_adder_4bit():
    """Test 4-bit ripple-carry adder across various integer additions."""
    test_cases = [
        (0, 0, 0),
        (3, 5, 0),    # 3 + 5 = 8
        (7, 8, 0),    # 7 + 8 = 15
        (7, 9, 0),    # 7 + 9 = 16 (overflow to c_out)
        (15, 15, 0),  # 15 + 15 = 30 (14 + carry)
        (6, 7, 1),    # 6 + 7 + c_in(1) = 14
        (15, 0, 1),   # 15 + 0 + 1 = 16
    ]

    for num_a, num_b, cin_val in test_cases:
        agenda = make_agenda()
        a_bus = make_bus(4, "A")
        b_bus = make_bus(4, "B")
        sum_bus = make_bus(4, "S")
        c_out = make_wire("c_out")
        c_in = make_wire("c_in")

        ripple_carry_adder(a_bus, b_bus, sum_bus, c_out, c_in=c_in, agenda=agenda)
        set_bus_values(a_bus, num_a)
        set_bus_values(b_bus, num_b)
        set_signal(c_in, cin_val)
        propagate(agenda)

        expected_total = num_a + num_b + cin_val
        expected_sum_bits = [(expected_total >> i) & 1 for i in range(4)]
        expected_cout_bit = (expected_total >> 4) & 1

        assert get_bus_values(sum_bus) == expected_sum_bits, f"Failed {num_a} + {num_b} + {cin_val}"
        assert get_signal(c_out) == expected_cout_bit, f"Failed c_out for {num_a} + {num_b} + {cin_val}"


def test_multiplexer():
    agenda = make_agenda()
    a = make_wire("a")
    b = make_wire("b")
    sel = make_wire("sel")
    out = make_wire("out")

    multiplexer(a, b, sel, out, agenda=agenda)

    # sel=0 -> out follows a
    set_signal(a, 1)
    set_signal(b, 0)
    set_signal(sel, 0)
    propagate(agenda)
    assert get_signal(out) == 1

    # sel=1 -> out follows b
    set_signal(sel, 1)
    propagate(agenda)
    assert get_signal(out) == 0

    set_signal(b, 1)
    propagate(agenda)
    assert get_signal(out) == 1


def test_demultiplexer():
    agenda = make_agenda()
    in_w = make_wire("in")
    sel = make_wire("sel")
    out_a = make_wire("out_a")
    out_b = make_wire("out_b")

    demultiplexer(in_w, sel, out_a, out_b, agenda=agenda)

    set_signal(in_w, 1)
    set_signal(sel, 0)
    propagate(agenda)
    assert get_signal(out_a) == 1
    assert get_signal(out_b) == 0

    set_signal(sel, 1)
    propagate(agenda)
    assert get_signal(out_a) == 0
    assert get_signal(out_b) == 1
