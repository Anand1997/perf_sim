"""Tests for the SimPy-backed agenda, clock generator, and sequential circuits."""

import pytest
from circuit_sim import (
    SIMPY_AVAILABLE,
    SimPyAgenda,
    clock_generator,
    d_flip_flop,
    full_adder,
    get_bus_values,
    get_signal,
    half_adder,
    make_bus,
    make_probe_recorder,
    make_realtime_agenda,
    make_simpy_agenda,
    make_wire,
    probe,
    pulse_generator,
    ripple_carry_adder,
    set_bus_values,
    set_signal,
    signal_schedule,
    sr_latch,
)


@pytest.mark.skipif(not SIMPY_AVAILABLE, reason="SimPy is not installed")
def test_simpy_agenda_basic_scheduling():
    agenda = make_simpy_agenda()
    assert agenda.is_empty() is True
    assert agenda.get_current_time() == 0

    trace = []
    agenda.after_delay(5, lambda: trace.append(("t5", agenda.get_current_time())))
    agenda.after_delay(2, lambda: trace.append(("t2", agenda.get_current_time())))
    agenda.add_to_agenda(8, lambda: trace.append(("t8", agenda.get_current_time())))

    assert agenda.is_empty() is False
    agenda.propagate()

    assert agenda.is_empty() is True
    assert agenda.get_current_time() == 8
    assert trace == [("t2", 2), ("t5", 5), ("t8", 8)]


@pytest.mark.skipif(not SIMPY_AVAILABLE, reason="SimPy is not installed")
def test_simpy_agenda_step_limit():
    agenda = make_simpy_agenda()
    trace = []

    agenda.after_delay(1, lambda: trace.append(1))
    agenda.after_delay(2, lambda: trace.append(2))
    agenda.after_delay(3, lambda: trace.append(3))

    agenda.propagate(step_limit=2)
    assert trace == [1, 2]
    assert not agenda.is_empty()

    agenda.propagate()
    assert trace == [1, 2, 3]
    assert agenda.is_empty()


@pytest.mark.skipif(not SIMPY_AVAILABLE, reason="SimPy is not installed")
def test_simpy_agenda_sicp_half_adder_trace():
    """Verify exact SICP timing trace using SimPy engine."""
    agenda = make_simpy_agenda()
    input_1 = make_wire("input-1")
    input_2 = make_wire("input-2")
    sum_wire = make_wire("sum")
    carry_wire = make_wire("carry")

    recorder = make_probe_recorder()
    probe("sum", sum_wire, agenda=agenda, callback=recorder.callback)
    probe("carry", carry_wire, agenda=agenda, callback=recorder.callback)

    half_adder(input_1, input_2, sum_wire, carry_wire, agenda=agenda)

    # Initial states
    assert ("sum", 0, 0) in recorder.transitions
    assert ("carry", 0, 0) in recorder.transitions

    # Step 1: input-1 = 1
    recorder.clear()
    set_signal(input_1, 1)
    agenda.propagate()

    assert recorder.transitions == [("sum", 8, 1)]
    assert get_signal(sum_wire) == 1
    assert get_signal(carry_wire) == 0

    # Step 2: input-2 = 1
    recorder.clear()
    set_signal(input_2, 1)
    agenda.propagate()

    assert recorder.transitions == [("carry", 11, 1), ("sum", 16, 0)]
    assert get_signal(sum_wire) == 0
    assert get_signal(carry_wire) == 1


@pytest.mark.skipif(not SIMPY_AVAILABLE, reason="SimPy is not installed")
def test_simpy_ripple_carry_adder_8bit():
    """Test 8-bit addition with SimPy engine."""
    agenda = make_simpy_agenda()
    a_bus = make_bus(8, "A")
    b_bus = make_bus(8, "B")
    sum_bus = make_bus(8, "S")
    c_out = make_wire("Cout")
    c_in = make_wire("Cin")

    ripple_carry_adder(a_bus, b_bus, sum_bus, c_out, c_in=c_in, agenda=agenda)

    # 45 + 55 = 100
    set_bus_values(a_bus, 45)
    set_bus_values(b_bus, 55)
    set_signal(c_in, 0)
    agenda.propagate()

    sum_bits = get_bus_values(sum_bus)
    total = sum(b << i for i, b in enumerate(sum_bits))
    assert total == 100
    assert get_signal(c_out) == 0


@pytest.mark.skipif(not SIMPY_AVAILABLE, reason="SimPy is not installed")
def test_simpy_clock_generator():
    agenda = make_simpy_agenda()
    clk = make_wire("CLK")
    recorder = make_probe_recorder()
    probe("CLK", clk, agenda=agenda, callback=recorder.callback)

    clock_generator(agenda, clk, high_duration=10, low_duration=10, initial_value=0, cycles=3)
    agenda.propagate()

    # Initial 0 at t=0, transitions at 10 (1), 20 (0), 30 (1), 40 (0), 50 (1), 60 (0)
    assert recorder.transitions == [
        ("CLK", 0, 0),
        ("CLK", 10, 1),
        ("CLK", 20, 0),
        ("CLK", 30, 1),
        ("CLK", 40, 0),
        ("CLK", 50, 1),
        ("CLK", 60, 0),
    ]


@pytest.mark.skipif(not SIMPY_AVAILABLE, reason="SimPy is not installed")
def test_simpy_pulse_generator_and_schedule():
    agenda = make_simpy_agenda()
    w1 = make_wire("W1")
    w2 = make_wire("W2")

    recorder = make_probe_recorder()
    probe("W1", w1, agenda=agenda, callback=recorder.callback)
    probe("W2", w2, agenda=agenda, callback=recorder.callback)

    pulse_generator(agenda, w1, sequence=[(5, 1), (10, 0), (15, 1)])
    signal_schedule(agenda, w2, schedule=[(7, 1), (14, 0)])

    agenda.propagate()

    w1_events = [(e.name, e.time, e.value) for e in recorder.events if e.name == "W1"]
    w2_events = [(e.name, e.time, e.value) for e in recorder.events if e.name == "W2"]

    assert w1_events == [("W1", 0, 0), ("W1", 0, 1), ("W1", 5, 0), ("W1", 15, 1)]
    assert w2_events == [("W2", 0, 0), ("W2", 7, 1), ("W2", 14, 0)]


@pytest.mark.skipif(not SIMPY_AVAILABLE, reason="SimPy is not installed")
def test_simpy_sr_latch():
    agenda = make_simpy_agenda()
    s = make_wire("S")
    r = make_wire("R")
    q = make_wire("Q")
    q_bar = make_wire("Q_bar")

    sr_latch(s, r, q, q_bar, agenda=agenda)

    # Set condition (S=1, R=0)
    set_signal(s, 1)
    set_signal(r, 0)
    agenda.propagate()
    assert get_signal(q) == 1
    assert get_signal(q_bar) == 0

    # Hold condition (S=0, R=0) -> preserves state
    set_signal(s, 0)
    agenda.propagate()
    assert get_signal(q) == 1
    assert get_signal(q_bar) == 0

    # Reset condition (S=0, R=1)
    set_signal(r, 1)
    agenda.propagate()
    assert get_signal(q) == 0
    assert get_signal(q_bar) == 1


@pytest.mark.skipif(not SIMPY_AVAILABLE, reason="SimPy is not installed")
def test_realtime_agenda():
    rt_agenda = make_realtime_agenda(factor=0.001)
    assert repr(rt_agenda).startswith("SimPyAgenda")
    w = make_wire("rt_w")
    rt_agenda.after_delay(2, lambda: set_signal(w, 1))
    rt_agenda.propagate()
    assert get_signal(w) == 1
